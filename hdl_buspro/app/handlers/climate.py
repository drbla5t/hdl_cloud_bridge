def handle_climate_command(device, payload):
    action = payload.get("_topic_action")
    raw_value = str(payload.get("value", "")).strip().lower()

    if action == "mode_set":
        mode_map = {
            "off": ("on_off", "off"),
            "cool": ("mode", "cool"),
            "heat": ("mode", "heat"),
            "dry": ("mode", "dry"),
            "fan_only": ("mode", "fan"),
            "auto": ("mode", "auto"),
        }

        if raw_value not in mode_map:
            print(f"Unsupported climate mode: {raw_value}")
            return None

        key, value = mode_map[raw_value]
        return {"key": key, "value": value}

    if action == "temp_set":
        return {
            "key": "set_temp",
            "value": str(payload.get("value")),
        }

    if action == "fan_mode_set":
        fan_map = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "auto": "auto",
        }

        if raw_value not in fan_map:
            print(f"Unsupported fan mode: {raw_value}")
            return None

        return {"key": "fan", "value": fan_map[raw_value]}

    if action == "set":
        return {
            "key": "on_off",
            "value": "on" if raw_value in ["on", "1", "true"] else "off",
        }

    print(f"Unsupported climate action: {action}")
    return None