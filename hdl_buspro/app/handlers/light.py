def _truthy(value):
    return str(value).strip().lower() in {"on", "1", "true", "yes"}


def _attr_keys(device):
    return {a.get("key") for a in device.get("attributes", []) if isinstance(a, dict)}


def _clamp(value, min_v, max_v):
    return max(min_v, min(max_v, value))


def handle_light_command(device, payload):
    if not isinstance(payload, dict):
        return None

    attr_keys = _attr_keys(device)
    spk = device.get("spk", "")

    if "state" in payload and payload.get("state") is not None:
        return {
            "key": "on_off",
            "value": "on" if _truthy(payload["state"]) else "off",
        }

    if "value" in payload and payload.get("value") is not None:
        raw_value = payload.get("value")
        if str(raw_value).strip().lower() in {"on", "off", "1", "0", "true", "false"}:
            return {
                "key": "on_off",
                "value": "on" if _truthy(raw_value) else "off",
            }

    if "brightness" in payload and "brightness" in attr_keys:
        try:
            brightness_255 = int(payload["brightness"])
            brightness_pct = round((brightness_255 / 255) * 100)
            brightness_pct = _clamp(brightness_pct, 0, 100)
            return {
                "key": "brightness",
                "value": str(brightness_pct),
            }
        except Exception:
            return None

    if "color_temp" in payload and "cct" in attr_keys:
        try:
            mireds = int(payload["color_temp"])
            kelvin = round(1000000 / mireds)
            kelvin = _clamp(kelvin, 2700, 6500)
            return {
                "key": "cct",
                "value": str(kelvin),
            }
        except Exception:
            return None

    if "rgbw" in payload and "rgbw" in attr_keys:
        try:
            rgbw = payload["rgbw"]
            if not isinstance(rgbw, (list, tuple)) or len(rgbw) != 4:
                return None

            r, g, b, w = [int(x) for x in rgbw]
            r = _clamp(r, 0, 255)
            g = _clamp(g, 0, 255)
            b = _clamp(b, 0, 255)
            w = _clamp(w, 0, 255)

            return {
                "key": "rgbw",
                "value": f"{r},{g},{b},{w}",
            }
        except Exception:
            return None

    if "rgb_color" in payload and "rgbw" in attr_keys and spk == "light.rgbw":
        try:
            rgb = payload["rgb_color"]
            if not isinstance(rgb, (list, tuple)) or len(rgb) != 3:
                return None

            r, g, b = [int(x) for x in rgb]
            r = _clamp(r, 0, 255)
            g = _clamp(g, 0, 255)
            b = _clamp(b, 0, 255)

            return {
                "key": "rgbw",
                "value": f"{r},{g},{b},0",
            }
        except Exception:
            return None

    return None
1