def publish(mqtt, uid, status):
    raw_on_off = status.get("on_off", "off")
    raw_mode = status.get("mode", "auto")
    raw_fan = status.get("fan", "auto")
    raw_set_temp = status.get("set_temp")
    raw_room_temp = status.get("room_temp")

    mode_map = {
        "cool": "cool",
        "heat": "heat",
        "dry": "dry",
        "fan": "fan_only",
        "auto": "auto",
    }

    ha_mode = "off" if raw_on_off != "on" else mode_map.get(raw_mode, "auto")

    mqtt.publish(f"hdl/{uid}/mode/state", ha_mode, retain=True)
    mqtt.publish(f"hdl/{uid}/fan/state", raw_fan, retain=True)

    if raw_set_temp is not None:
        mqtt.publish(f"hdl/{uid}/temp/state", str(raw_set_temp), retain=True)

    if raw_room_temp is not None:
        mqtt.publish(f"hdl/{uid}/current_temp/state", str(raw_room_temp), retain=True)