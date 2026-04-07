def publish(mqtt, uid, status, device):
    spk = device.get("spk", "")

    if spk == "hvac.floorHeat":
        raw_on_off = status.get("on_off", "off")
        raw_mode_work = status.get("mode_work", "heat")
        raw_preset = status.get("mode", "normal")
        raw_set_temp = status.get("set_temp")
        raw_room_temp = status.get("room_temp")

        mode_map = {
            "heat": "heat",
            "cool": "cool",
            "economic": "eco",
        }

        payload = {
            "mode": "off" if raw_on_off != "on" else mode_map.get(raw_mode_work, "heat"),
            "preset_mode": raw_preset,
        }

        if raw_set_temp is not None:
            try:
                payload["temperature"] = float(raw_set_temp)
            except Exception:
                pass

        if raw_room_temp is not None:
            try:
                payload["current_temperature"] = float(raw_room_temp)
            except Exception:
                pass

        mqtt.publish(f"hdl/{uid}/state", payload, retain=True)
        return

    raw_on_off = status.get("on_off", "off")
    raw_mode = status.get("mode", "auto")
    raw_fan = status.get("fan", "auto")
    raw_swing = status.get("swing", "stop")
    raw_set_temp = status.get("set_temp")
    raw_room_temp = status.get("room_temp")

    mode_map = {
        "cool": "cool",
        "heat": "heat",
        "dry": "dry",
        "fan": "fan_only",
        "auto": "auto",
    }

    swing_map = {
        "stop": "off",
        "up_down": "vertical",
        "left_right": "horizontal",
    }

    payload = {
        "mode": "off" if raw_on_off != "on" else mode_map.get(raw_mode, "auto"),
        "fan_mode": raw_fan,
        "swing_mode": swing_map.get(raw_swing, "off"),
    }

    if raw_set_temp is not None:
        try:
            payload["temperature"] = float(raw_set_temp)
        except Exception:
            pass

    if raw_room_temp is not None:
        try:
            payload["current_temperature"] = float(raw_room_temp)
        except Exception:
            pass

    mqtt.publish(f"hdl/{uid}/state", payload, retain=True)