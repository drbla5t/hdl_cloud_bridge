def publish(mqtt, uid, status, device):
    state = "ON" if status.get("on_off") == "on" else "OFF"
    mqtt.publish(f"hdl/{uid}/state", state, retain=True)
    1