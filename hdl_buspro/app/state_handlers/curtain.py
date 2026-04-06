def publish(mqtt, uid, status, device):
    raw = status.get("on_off", "stop")
    percent = status.get("percent")

    state_map = {
        "on": "OPEN",
        "off": "CLOSED",
        "stop": "STOPPED",
    }

    payload = {
        "state": state_map.get(raw, "STOPPED"),
    }

    if percent is not None:
        try:
            payload["position"] = int(float(percent))
        except Exception:
            pass

    mqtt.publish(
        f"hdl/{uid}/state",
        payload,
        retain=True,
    )
    1