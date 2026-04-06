from app.registry import DEVICE_REGISTRY


class CommandRouter:
    def handle(self, device, payload):
        if not isinstance(device, dict):
            print("Invalid device object")
            return None

        if payload is None:
            print("Empty payload")
            return None

        spk = device.get("spk")
        if not spk:
            print("Device without spk")
            return None

        spec = self._resolve_spec(spk)
        if not spec:
            print(f"Unsupported spk: {spk}")
            return None

        handler = spec.get("command")
        if not handler:
            print(f"No command handler for spk: {spk}")
            return None

        try:
            return handler(device, payload)
        except Exception as e:
            print(f"Command handler error for spk={spk}: {e}")
            return None

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
    1