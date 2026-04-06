def handle_curtain_command(device, payload):
    if not isinstance(payload, dict):
        return None

    action = payload.get("_topic_action")
    raw_value = str(payload.get("value", "")).strip().lower()

    if action == "position_set":
        try:
            pos = int(payload.get("value"))
            pos = max(0, min(100, pos))
            return {
                "key": "percent",
                "value": str(pos),
            }
        except Exception:
            return None

    if raw_value == "open":
        value = "on"
    elif raw_value == "close":
        value = "off"
    elif raw_value == "stop":
        value = "stop"
    else:
        return None

    return {
        "key": "on_off",
        "value": value,
    }