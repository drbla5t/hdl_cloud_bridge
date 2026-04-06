def handle_climate_command(device, payload):
    if not isinstance(payload, dict):
        return None

    spk = device.get("spk", "")
    action = payload.get("_topic_action")
    raw_value = str(payload.get("value", "")).strip().lower()

    if spk == "hvac.floorHeat":
        if action == "mode_set":
            mode_map = {
                "off": ("on_off", "off"),
                "heat": ("mode_work", "heat"),
                "cool": ("mode_work", "cool"),
                "eco": ("mode_work", "economic"),
            }

            if raw_value not in mode_map:
                return None

            key, value = mode_map[raw_value]
            return {"key": key, "value": value}

        if action == "preset_mode_set":
            preset_map = {
                "day": "day",
                "night": "night",
                "away": "away",
                "normal": "normal",
                "timer": "timer",
            }

            if raw_value not in preset_map:
                return None

            return {
                "key": "mode",
                "value": preset_map[raw_value],
            }

        if action == "temp_set":
            return {
                "key": "set_temp",
                "value": str(payload.get("value")),
            }

        if action == "set":
            return {
                "key": "on_off",
                "value": "on" if raw_value in ["on", "1", "true"] else "off",
            }

        return None

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
            return None

        return {"key": "fan", "value": fan_map[raw_value]}

    if action == "swing_mode_set":
        swing_map = {
            "off": "stop",
            "vertical": "up_down",
            "horizontal": "left_right",
        }

        if raw_value not in swing_map:
            return None

        return {"key": "swing", "value": swing_map[raw_value]}

    if action == "set":
        return {
            "key": "on_off",
            "value": "on" if raw_value in ["on", "1", "true"] else "off",
        }

    return None