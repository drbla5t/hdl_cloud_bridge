from app.registry import DEVICE_REGISTRY


class Discovery:
    def __init__(self, mqtt):
        self.mqtt = mqtt

    def publish(self, device):
        spk = device.get("spk")
        uid = device.get("deviceIotId") or device.get("deviceId")
        if not uid:
            return

        spec = DEVICE_REGISTRY.get(spk)
        if not spec:
            return

        builder = spec.get("discovery")
        if not builder:
            return

        name = device.get("name", uid)
        cfg = builder(uid, name)

        cfg["payload"]["device"] = self._device(device)

        self.mqtt.publish(
            cfg["topic"],
            cfg["payload"],
            retain=True,
        )

    def _device(self, device):
        uid = device.get("deviceIotId") or device.get("deviceId")
        name = device.get("name", uid)
        model = device.get("omodel", "Buspro")
        home_name = device.get("_home_name", "HDL")

        return {
            "identifiers": [f"hdl_dev_{uid}"],
            "name": name,
            "manufacturer": home_name,
            "model": model,
        }