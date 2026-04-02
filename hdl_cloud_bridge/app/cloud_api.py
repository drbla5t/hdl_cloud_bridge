import hashlib
import time
from typing import Any, Dict, List

import requests

from models import DeviceInfo, ProjectInfo


class HdlCloudApi:
    def __init__(self, base_url: str, app_key: str, app_secret: str, home_id: int):
        self.base_url = base_url.rstrip("/")
        self.app_key = app_key
        self.app_secret = app_secret
        self.home_id = home_id

    def _flatten_for_sign(self, data: Dict[str, Any]) -> Dict[str, str]:
        flat: Dict[str, str] = {}
        for k, v in data.items():
            if isinstance(v, (str, int, float, bool)) and v is not None:
                flat[k] = str(v).lower() if isinstance(v, bool) else str(v)
        return flat

    def _make_sign(self, payload: Dict[str, Any]) -> str:
        flat = self._flatten_for_sign(payload)
        parts = [f"{k}={flat[k]}" for k in sorted(flat.keys())]
        sign_src = "&".join(parts) + self.app_secret
        return hashlib.md5(sign_src.encode("utf-8")).hexdigest()

    def post_json(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = dict(body)
        body["appKey"] = self.app_key
        body["timestamp"] = int(time.time() * 1000)
        body["sign"] = self._make_sign(body)

        resp = requests.post(url, json=body, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_projects(self) -> List[ProjectInfo]:
        result = self.post_json(
            "/smart-open/cloud/project/pageByApplication",
            {"pageNo": 1, "pageSize": 50},
        )
        projects = []
        for item in result.get("data", {}).get("list", []):
            projects.append(
                ProjectInfo(
                    project_id=item["communityId"],
                    name=item.get("communityName", ""),
                    protocol_type=item.get("protocolType", ""),
                    raw=item,
                )
            )
        return projects

    def get_devices_by_project(self, project_id: str) -> List[DeviceInfo]:
        result = self.post_json(
            "/smart-open/cloud/project/devicePage",
            {"projectId": project_id, "pageNo": 1, "pageSize": 200},
        )
        devices = []
        for item in result.get("data", {}).get("list", []):
            devices.append(
                DeviceInfo(
                    device_iot_id=item["deviceIotId"],
                    gateway_id=item.get("gatewayId", ""),
                    sid=item.get("sid", ""),
                    name=item.get("name", ""),
                    spk=item.get("spk", ""),
                    model=item.get("omodel", ""),
                    online=bool(item.get("online", False)),
                    attributes=item.get("attributes", []),
                    status=item.get("status"),
                    mac=item.get("mac"),
                    raw=item,
                )
            )
        return devices

    def control_switch(self, device: DeviceInfo, state: str) -> Dict[str, Any]:
        value = "on" if state.lower() == "on" else "off"

        body = {
            "homeId": self.home_id,
            "actions": [
                {
                    "deviceIotId": device.device_iot_id,
                    "spk": device.spk,
                    "sid": device.sid,
                    "attributes": [
                        {
                            "key": "on_off",
                            "value": value
                        }
                    ]
                }
            ]
        }

        return self.post_json("/smart-open/cloud/home/device/open/control", body)