def handle_light_command(device, payload):
    raw_value = str(payload.get("value", "")).strip().lower()

    return {
        "key": "on_off",
        "value": "on" if raw_value in ["on", "1", "true"] else "off",
    }