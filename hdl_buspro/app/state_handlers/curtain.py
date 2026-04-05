def publish(mqtt, uid, status):
    raw = status.get("on_off", "stop")

    state_map = {
        "on": "OPEN",
        "off": "CLOSED",
        "stop": "STOPPED",
    }

    mqtt.publish(
        f"hdl/{uid}/state",
        state_map.get(raw, "STOPPED"),
        retain=True,
    )