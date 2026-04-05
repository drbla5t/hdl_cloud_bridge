import json
from app.registry import DEVICE_REGISTRY


class StatePublisher:
    def __init__(self, mqtt):
        self.mqtt = mqtt

    def publish(self, device):
        uid = device.get("deviceIotId") or device.get("deviceId")
        if not uid:
            return

        status = {item["key"]: item["value"] for item in device.get("status", [])}
        spk = device.get("spk")

        self.mqtt.publish(
            f"hdl/{uid}/availability",
            "online" if device.get("online") else "offline",
            retain=True,
        )

        spec = DEVICE_REGISTRY.get(spk)
        if not spec:
            self.mqtt.publish(
                f"hdl/{uid}/raw_state",
                json.dumps(status, ensure_ascii=False),
                retain=True,
            )
            return

        handler = spec.get("state")
        if not handler:
            self.mqtt.publish(
                f"hdl/{uid}/raw_state",
                json.dumps(status, ensure_ascii=False),
                retain=True,
            )
            return

        handler(self.mqtt, uid, status)