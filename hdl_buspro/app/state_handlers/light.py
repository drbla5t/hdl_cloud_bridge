def _to_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return default


def publish(mqtt, uid, status, device):
    payload = {
        "state": "ON" if status.get("on_off") == "on" else "OFF",
    }

    if "brightness" in status:
        brightness_pct = _to_int(status.get("brightness"), 0)
        brightness_pct = max(0, min(100, brightness_pct))
        payload["brightness"] = round((brightness_pct / 100) * 255)

    if "cct" in status:
        kelvin = _to_int(status.get("cct"), 6500)
        if kelvin > 0:
            payload["color_temp"] = round(1000000 / kelvin)

    if "rgbw" in status:
        try:
            parts = [int(x.strip()) for x in str(status["rgbw"]).split(",")]
            if len(parts) == 4:
                payload["rgbw"] = parts
                payload["rgb_color"] = parts[:3]
        except Exception:
            pass

    mqtt.publish(f"hdl/{uid}/state", payload, retain=True)
    1