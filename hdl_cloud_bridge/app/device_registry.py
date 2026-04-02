from typing import Dict, List, Optional

from models import DeviceInfo


class DeviceRegistry:
    def __init__(self):
        self.by_id: Dict[str, DeviceInfo] = {}

    def replace(self, devices: List[DeviceInfo]) -> None:
        self.by_id = {d.device_iot_id: d for d in devices}

    def get(self, device_iot_id: str) -> Optional[DeviceInfo]:
        return self.by_id.get(device_iot_id)

    def all(self) -> List[DeviceInfo]:
        return list(self.by_id.values())