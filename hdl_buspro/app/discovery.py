from app.registry import DEVICE_REGISTRY


class Discovery:
    def __init__(self, mqtt):
        self.mqtt = mqtt

    def publish(self, device):
        if not isinstance(device, dict):
            return

        spk = device.get("spk")
        uid = device.get("deviceIotId") or device.get("deviceId")
        if not uid or not spk:
            return

        spec = self._resolve_spec(spk)
        if not spec:
            print(f"No discovery spec for spk: {spk}")
            return

        builder = spec.get("discovery")
        if not builder:
            print(f"No discovery builder for spk: {spk}")
            return

        try:
            cfg = builder(device)
        except Exception as e:
            print(f"Discovery builder error for spk={spk}: {e}")
            return

        if not cfg:
            return

        payload = cfg.get("payload", {})
        payload["device"] = self._device(device)

        self.mqtt.publish(
            cfg["topic"],
            payload,
            retain=True,
        )

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

    def _device(self, device):
        uid = device.get("deviceIotId") or device.get("deviceId")
        name = device.get("name", uid)

        manufacturer = (
            device.get("productBrand")
            or "HDL"
        )

        model = (
            device.get("productName")
            or device.get("omodel")
            or device.get("spk")
            or "Buspro"
        )

        info = {
            "identifiers": [f"hdl_dev_{uid}"],
            "name": name,
            "manufacturer": manufacturer,
            "model": model,
        }

        room_infos = device.get("roomInfos") or []
        if room_infos and isinstance(room_infos, list):
            room_name = room_infos[0].get("roomName")
            if room_name:
                info["suggested_area"] = room_name

        return info