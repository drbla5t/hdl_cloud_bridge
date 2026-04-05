import requests
import time
import hashlib
import json


BASE_URL = "https://ru-gateway.hdlcontrol.com"
APP_KEY = "CXZMMOCF"
SECRET = "CXZMMOCVCXZMMODL"
POLL_INTERVAL = 5

def _is_signable(value):
    return isinstance(value, (str, int, float, bool)) and value != ""


def _sign(data):
    data = dict(data)
    data["appKey"] = APP_KEY
    data["timestamp"] = str(int(time.time() * 1000))

    sign_items = []
    for key in sorted(data.keys()):
        value = data[key]
        if _is_signable(value):
            if isinstance(value, bool):
                value = str(value).lower()
            else:
                value = str(value)
            sign_items.append(f"{key}={value}")

    sign_src = "&".join(sign_items) + SECRET
    data["sign"] = hashlib.md5(sign_src.encode("utf-8")).hexdigest()
    return data


class HDLClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

    def api_post(self, endpoint, payload, auth=True):
        url = BASE_URL + endpoint
        payload = _sign(payload)

        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        r = requests.post(url, json=payload, headers=headers, timeout=30)

        print(f"{endpoint} -> {r.status_code} | {r.text[:200]}")

        r.raise_for_status()
        return r.json()


    def login(self):
        print("🔐 Login...")

        data = {
            "account": self.username,
            "loginPwd": self.password,
            "grantType": "password"
        }

        res = self.api_post(
            "/smart-footstone/member/oauth/login",
            data,
            auth=False
        )

        print("LOGIN RESPONSE:")
        print(json.dumps(res, ensure_ascii=False, indent=2))

        if res.get("code") != 0 or not res.get("data"):
            raise RuntimeError(f"Login failed: {res}")

        self.token = res["data"]["accessToken"]

        print("✅ Logged in")

    def get_homes(self):
        res = self.api_post("/home-wisdom/app/home/list", {
            "homeType": "ALL",
            "autoGenerate": False
        })
        return res["data"]

    def get_devices(self, home_id):
        res = self.api_post("/home-wisdom/app/device/list", {
            "homeId": home_id,
            "pageNo": 1,
            "pageSize": 200
        })
        return res.get("data", {}).get("list", [])

    def control(self, home_id, gateway_id, device, key, value):
        attr = next((a for a in device.get("attributes", []) if a.get("key") == key), None)
        data_type = attr.get("data_type", "string") if attr else "string"

        payload = {
            "homeId": home_id,
            "gatewayId": gateway_id,
            "actions": [
                {
                    "deviceId": device["deviceId"],
                    "spk": device["spk"],
                    "attributes": [
                        {
                            "key": key,
                            "value": str(value),
                            "data_type": data_type,
                        }
                    ]
                }
            ]
        }

        print("HDL CONTROL REQUEST:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        res = self.api_post("/home-wisdom/app/device/control", payload)

        print("HDL CONTROL RESPONSE:")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res
