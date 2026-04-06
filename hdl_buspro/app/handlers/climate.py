def handle_climate_command(device, payload):
    if not isinstance(payload, dict):
        return None

    spk = device.get("spk", "")
    action = payload.get("_topic_action")
    raw_value = str(payload.get("value", "")).strip().lower()

    status = {item["key"]: item["value"] for item in device.get("status", []) if isinstance(item, dict)}
    is_on = status.get("on_off") == "on"

    if spk == "hvac.floorHeat":
        if action == "mode_set":
            mode_map = {
                "off": [{"key": "on_off", "value": "off"}],
                "heat": [{"key": "on_off", "value": "on"}, {"key": "mode_work", "value": "heat"}],
                "cool": [{"key": "on_off", "value": "on"}, {"key": "mode_work", "value": "cool"}],
                "eco": [{"key": "on_off", "value": "on"}, {"key": "mode_work", "value": "economic"}],
            }
            return mode_map.get(raw_value)

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
            return {"key": "mode", "value": preset_map[raw_value]}

        if action == "temp_set":
            return {"key": "set_temp", "value": str(payload.get("value"))}

        if action == "set":
            return {"key": "on_off", "value": "on" if raw_value in ["on", "1", "true"] else "off"}

        return None

    if action == "mode_set":
        mode_map = {
            "off": [{"key": "on_off", "value": "off"}],
            "cool": [{"key": "on_off", "value": "on"}, {"key": "mode", "value": "cool"}],
            "heat": [{"key": "on_off", "value": "on"}, {"key": "mode", "value": "heat"}],
            "dry": [{"key": "on_off", "value": "on"}, {"key": "mode", "value": "dry"}],
            "fan_only": [{"key": "on_off", "value": "on"}, {"key": "mode", "value": "fan"}],
            "auto": [{"key": "on_off", "value": "on"}, {"key": "mode", "value": "auto"}],
        }
        return mode_map.get(raw_value)

    if action == "temp_set":
        return {"key": "set_temp", "value": str(payload.get("value"))}

    if action == "fan_mode_set":
        fan_map = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "auto": "auto",
        }
        if raw_value not in fan_map:
            return None

        if not is_on:
            return [
                {"key": "on_off", "value": "on"},
                {"key": "fan", "value": fan_map[raw_value]},
            ]

        return {"key": "fan", "value": fan_map[raw_value]}

    if action == "swing_mode_set":
        swing_map = {
            "off": "stop",
            "vertical": "up_down",
            "horizontal": "left_right",
        }
        if raw_value not in swing_map:
            return None

        if not is_on:
            return [
                {"key": "on_off", "value": "on"},
                {"key": "swing", "value": swing_map[raw_value]},
            ]

        return {"key": "swing", "value": swing_map[raw_value]}

    if action == "set":
        return {"key": "on_off", "value": "on" if raw_value in ["on", "1", "true"] else "off"}

    return None