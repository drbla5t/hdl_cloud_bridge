def _attr_keys(device):
    return {a.get("key") for a in device.get("attributes", []) if isinstance(a, dict)}


def build(device):
    uid = device.get("deviceIotId") or device.get("deviceId")
    name = device.get("name", uid)
    spk = device.get("spk", "")
    attr_keys = _attr_keys(device)

    payload = {
        "name": name,
        "unique_id": f"hdl_{uid}",
        "state_topic": f"hdl/{uid}/state",
        "command_topic": f"hdl/{uid}/set",
        "availability_topic": f"hdl/{uid}/availability",
        "payload_available": "online",
        "payload_not_available": "offline",
        "schema": "json",
        "brightness": "brightness" in attr_keys,
        "supported_color_modes": [],
    }

    if spk == "light.switch":
        payload["supported_color_modes"] = ["onoff"]
    elif spk == "light.dimming":
        payload["supported_color_modes"] = ["brightness"]
    elif spk == "light.cct":
        payload["supported_color_modes"] = ["color_temp"]
        payload["brightness"] = True
        payload["min_mireds"] = round(1000000 / 6500)
        payload["max_mireds"] = round(1000000 / 2700)
    elif spk == "light.rgbw":
        payload["supported_color_modes"] = ["rgbw"]
        payload["brightness"] = True
    else:
        if "rgbw" in attr_keys:
            payload["supported_color_modes"] = ["rgbw"]
            payload["brightness"] = True
        elif "cct" in attr_keys:
            payload["supported_color_modes"] = ["color_temp"]
            payload["brightness"] = True
            payload["min_mireds"] = round(1000000 / 6500)
            payload["max_mireds"] = round(1000000 / 2700)
        elif "brightness" in attr_keys:
            payload["supported_color_modes"] = ["brightness"]
            payload["brightness"] = True
        else:
            payload["supported_color_modes"] = ["onoff"]

    return {
        "topic": f"homeassistant/light/hdl_{uid}/config",
        "payload": payload,
    }