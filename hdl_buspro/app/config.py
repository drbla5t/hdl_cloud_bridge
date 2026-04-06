import os
import json

USERNAME = os.getenv("HDL_USERNAME", "")
PASSWORD = os.getenv("HDL_PASSWORD", "")

MQTT_HOST = os.getenv("MQTT_HOST", "core-mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASS = os.getenv("MQTT_PASS", "")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "15"))

HDL_SERVERS = {
    "ru": "https://ru-gateway.hdlcontrol.com",
    "china": "https://nearest.hdlcontrol.com",
    "bahrain": "https://bahrain-gateway.hdlcontrol.com",
}

HDL_SERVER = os.getenv("HDL_SERVER", "ru").strip().lower()

_raw_home_names = os.getenv("HDL_HOME_NAMES", "").strip()

try:
    parsed = json.loads(_raw_home_names) if _raw_home_names else []
    if isinstance(parsed, list):
        HDL_HOME_NAMES = [str(x).strip() for x in parsed if str(x).strip()]
    else:
        HDL_HOME_NAMES = []
except Exception:
    HDL_HOME_NAMES = [x.strip() for x in _raw_home_names.split(",") if x.strip()]