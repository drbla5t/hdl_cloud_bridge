from app.registry import DEVICE_REGISTRY


class CommandRouter:
    def handle(self, device, payload):
        spk = device.get("spk")
        spec = DEVICE_REGISTRY.get(spk)

        if not spec:
            print(f"Unsupported spk: {spk}")
            return None

        handler = spec.get("command")
        if not handler:
            print(f"No command handler for spk: {spk}")
            return None

        return handler(device, payload)