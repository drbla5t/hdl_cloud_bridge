import hashlib
import json
import time
import requests


APP_KEY = "CXZMMOCF"
SECRET = "CXZMMOCVCXZMMODL"


def _is_signable(value):
    return isinstance(value, (str, int, float, bool)) and value != ""


def _sign(data):
    data = dict(data or {})
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
    def __init__(self, username, password, servers, selected_server="ru"):
        self.username = username
        self.password = password
        self.servers = servers
        self.selected_server = selected_server

        self.base_url = None
        self.session = requests.Session()

        self.access_token = None
        self.refresh_token = None
        self.header_prefix = "Bearer "

    def _server_candidates(self):
        if self.selected_server == "auto":
            return [
                self.servers["ru"],
                self.servers["china"],
                self.servers["bahrain"],
            ]

        if self.selected_server not in self.servers:
            raise RuntimeError(
                f"Unknown HDL_SERVER='{self.selected_server}'. "
                f"Use one of: {', '.join(self.servers.keys())} or 'auto'"
            )

        return [self.servers[self.selected_server]]

    def _auth_headers(self, auth=True):
        headers = {"Content-Type": "application/json"}
        if auth and self.access_token:
            headers["Authorization"] = f"{self.header_prefix}{self.access_token}"
        return headers

    def _request(self, method, path, *, json_data=None, auth=True, retry=True):
        if not self.base_url:
            raise RuntimeError("HDL client is not initialized")

        url = f"{self.base_url}{path}"
        payload = _sign(json_data or {})

        try:
            resp = self.session.request(
                method=method,
                url=url,
                json=payload,
                headers=self._auth_headers(auth=auth),
                timeout=30,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed for {path}: {e}") from e

        text = resp.text
        print(f"{path} -> {resp.status_code} | {text[:300]}")

        try:
            data = resp.json()
        except Exception as e:
            raise RuntimeError(
                f"Non-JSON response for {path}: HTTP {resp.status_code}, body={text[:500]}"
            ) from e

        if auth and data.get("code") == 10001 and retry:
            print("⚠️ Session expired, trying relogin...")
            self.login()
            return self._request(
                method,
                path,
                json_data=json_data,
                auth=auth,
                retry=False,
            )

        return data

    def login(self):
        print("🔐 Login...")
        last_error = None

        for server in self._server_candidates():
            try:
                self.base_url = server.rstrip("/")
                print(f"Trying HDL server: {self.base_url}")

                payload = {
                    "account": self.username,
                    "loginPwd": self.password,
                    "grantType": "password",
                }

                data = self._request(
                    "POST",
                    "/smart-footstone/member/oauth/login",
                    json_data=payload,
                    auth=False,
                    retry=False,
                )

                print("LOGIN RESPONSE:")
                print(json.dumps(data, ensure_ascii=False, indent=2))

                if data.get("code") != 0 or not data.get("data"):
                    last_error = data
                    print(f"Login failed on {self.base_url}: {data}")
                    continue

                token_data = data["data"]
                self.access_token = token_data.get("accessToken")
                self.refresh_token = token_data.get("refreshToken")
                self.header_prefix = token_data.get("headerPrefix") or "Bearer "
                if not self.header_prefix.endswith(" "):
                    self.header_prefix += " "

                print(f"✅ Logged in via {self.base_url}")
                return

            except Exception as e:
                last_error = e
                print(f"Login error on {server}: {e}")

        raise RuntimeError(f"HDL login failed: {last_error}")

    def get_homes(self):
        data = self._request(
            "POST",
            "/home-wisdom/app/home/list",
            json_data={
                "homeType": "ALL",
                "autoGenerate": False,
            },
        )
        if data.get("code") != 0:
            raise RuntimeError(f"get_homes failed: {data}")
        return data.get("data", [])

    def get_devices(self, home_id):
        data = self._request(
            "POST",
            "/home-wisdom/app/device/list",
            json_data={
                "homeId": home_id,
                "pageNo": 1,
                "pageSize": 200,
            },
        )
        if data.get("code") != 0:
            raise RuntimeError(f"get_devices failed: {data}")
        return data.get("data", {}).get("list", [])

    def control(self, home_id, gateway_id, device, key, value):
        attr = next(
            (a for a in device.get("attributes", []) if a.get("key") == key),
            None,
        )
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
                    ],
                }
            ],
        }

        print("HDL CONTROL REQUEST:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        data = self._request(
            "POST",
            "/home-wisdom/app/device/control",
            json_data=payload,
        )

        print("HDL CONTROL RESPONSE:")
        print(json.dumps(data, ensure_ascii=False, indent=2))

        if data.get("code") != 0:
            raise RuntimeError(f"control failed: {data}")

        return data