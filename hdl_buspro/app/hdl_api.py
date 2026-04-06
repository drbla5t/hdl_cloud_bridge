import hashlib
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

    def _auth_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"{self.header_prefix}{self.access_token}"
        return headers

    def login(self):
        print("🔐 Login...")
        last_error = None

        login_variants = [
            {
                "account": self.username,
                "password": self.password,
                "grantType": "password",
            },
            {
                "account": self.username,
                "password": self.password,
                "grant_type": "password",
            },
            {
                "account": self.username,
                "password": self.password,
                "authType": "password",
            },
            {
                "account": self.username,
                "password": self.password,
                "loginType": "password",
            },
            {
                "account": self.username,
                "password": self.password,
            },
        ]

        for server in self._server_candidates():
            self.base_url = server.rstrip("/")
            print(f"Trying HDL server: {self.base_url}")

            for payload_base in login_variants:
                try:
                    url = f"{self.base_url}/smart-footstone/member/oauth/login"
                    payload = _sign(payload_base)

                    resp = self.session.post(
                        url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30,
                    )
                    print(f"/smart-footstone/member/oauth/login -> {resp.status_code}")

                    data = resp.json()

                    if data.get("code") == 0:
                        token_data = data["data"]
                        self.access_token = token_data.get("accessToken")
                        self.refresh_token = token_data.get("refreshToken")
                        self.header_prefix = token_data.get("headerPrefix") or "Bearer "
                        if not self.header_prefix.endswith(" "):
                            self.header_prefix += " "

                        print(f"✅ Logged in via {self.base_url}")
                        return

                    last_error = data
                    print(f"Login variant failed: {payload_base} -> {data}")

                except Exception as e:
                    last_error = e
                    print(f"Login error with payload {payload_base}: {e}")

        raise RuntimeError(f"HDL login failed: {last_error}")

    def refresh_access_token(self):
        if not self.refresh_token:
            print("No refresh token, relogin...")
            self.login()
            return

        print("🔄 Refresh token...")
        url = f"{self.base_url}/smart-footstone/member/oauth/refreshToken"
        payload = _sign({
            "refreshToken": self.refresh_token
        })

        try:
            resp = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            print(f"/smart-footstone/member/oauth/refreshToken -> {resp.status_code}")
            data = resp.json()
        except Exception as e:
            print(f"Refresh request failed: {e}")
            print("Refresh failed, relogin...")
            self.login()
            return

        if data.get("code") != 0:
            print(f"Refresh failed: {data}")
            print("Refresh failed, relogin...")
            self.login()
            return

        token_data = data["data"]
        self.access_token = token_data.get("accessToken")
        self.refresh_token = token_data.get("refreshToken", self.refresh_token)
        self.header_prefix = token_data.get("headerPrefix") or "Bearer "
        if not self.header_prefix.endswith(" "):
            self.header_prefix += " "

        print("✅ Token refreshed")

    def _request(self, method, path, *, json_data=None, retry=True):
        if not self.base_url:
            raise RuntimeError("HDL client is not logged in")

        url = f"{self.base_url}{path}"
        signed_payload = _sign(json_data or {})

        try:
            resp = self.session.request(
                method=method,
                url=url,
                json=signed_payload,
                headers=self._auth_headers(),
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

        if data.get("code") == 10001 and retry:
            print("⚠️ Session expired, refreshing token...")
            self.refresh_access_token()
            return self._request(method, path, json_data=json_data, retry=False)

        return data

    def get_homes(self):
        data = self._request("GET", "/home-wisdom/app/home/list")
        if data.get("code") != 0:
            raise RuntimeError(f"get_homes failed: {data}")
        return data.get("data", [])

    def get_devices(self, home_id):
        payload = {
            "homeId": home_id,
            "pageNum": 1,
            "pageSize": 500,
        }
        data = self._request("POST", "/home-wisdom/app/device/list", json_data=payload)
        if data.get("code") != 0:
            raise RuntimeError(f"get_devices failed: {data}")
        return data.get("data", {}).get("list", [])

    def control(self, home_id, gateway_id, device, key, value):
        payload = {
            "homeId": home_id,
            "gatewayId": gateway_id,
            "deviceId": device["deviceId"],
            "spk": device["spk"],
            "attributes": [
                {
                    "key": key,
                    "value": value,
                }
            ],
        }

        data = self._request("POST", "/home-wisdom/app/device/control", json_data=payload)
        if data.get("code") != 0:
            raise RuntimeError(f"control failed: {data}")
        return data