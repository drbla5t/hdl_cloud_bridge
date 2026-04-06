import json
from app.registry import DEVICE_REGISTRY


class StatePublisher:
    def __init__(self, mqtt):
        self.mqtt = mqtt

    def publish(self, device):
        if not isinstance(device, dict):
            return

        uid = device.get("deviceIotId") or device.get("deviceId")
        spk = device.get("spk")

        if not uid:
            return

        status = self._status_to_dict(device.get("status", []))

        self.mqtt.publish(
            f"hdl/{uid}/availability",
            "online" if device.get("online") else "offline",
            retain=True,
        )

        self.mqtt.publish(
            f"hdl/{uid}/raw_state",
            json.dumps(status, ensure_ascii=False),
            retain=True,
        )

        if not spk:
            return

        spec = self._resolve_spec(spk)
        if not spec:
            return

        handler = spec.get("state")
        if not handler:
            return

        try:
            handler(self.mqtt, uid, status, device)
        except Exception as e:
            print(f"State handler error for spk={spk}: {e}")

    def _resolve_spec(self, spk):
        spec = DEVICE_REGISTRY.get(spk)
        if spec:
            return spec

        if spk.startswith("light."):
            return DEVICE_REGISTRY.get("light.*")

        if spk.startswith("curtain."):
            return DEVICE_REGISTRY.get("curtain.*")

        if spk.startswith("hvac."):
            return DEVICE_REGISTRY.get("hvac.*")

        if spk.startswith("other."):
            return DEVICE_REGISTRY.get("other.*")

        return None

    @staticmethod
    def _status_to_dict(status_items):
        result = {}

        if not isinstance(status_items, list):
            return result

        for item in status_items:
            if not isinstance(item, dict):
                continue

            key = item.get("key")
            value = item.get("value")

            if key is None:
                continue

            result[key] = value

        return result
    1