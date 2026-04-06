def handle_generic_command(device, payload):
    if not isinstance(payload, dict):
        return None

    raw_value = str(payload.get("value", "")).strip().lower()

    return {
        "key": "on_off",
        "value": "on" if raw_value in ["on", "1", "true"] else "off",
    }
1