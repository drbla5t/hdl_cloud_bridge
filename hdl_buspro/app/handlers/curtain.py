def handle_curtain_command(device, payload):
    raw_value = str(payload.get("value", "")).strip().lower()

    if raw_value == "open":
        value = "on"
    elif raw_value == "close":
        value = "off"
    else:
        value = "stop"

    return {
        "key": "on_off",
        "value": value,
    }