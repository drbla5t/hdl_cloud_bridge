import os

USERNAME = os.getenv("HDL_USER", "")
PASSWORD = os.getenv("HDL_PASS", "")

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.25")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASS = os.getenv("MQTT_PASS", "")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

HDL_HOME_NAMES = [
    x.strip() for x in os.getenv("HDL_HOME_NAMES", "").split(",") if x.strip()
]