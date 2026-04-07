def map_state(device):
    state = {s["key"]: s["value"] for s in device.get("status", [])}

    spk = device.get("spk")

    if spk == "light.switch":
        return {"state": "ON" if state.get("on_off") == "on" else "OFF"}

    if spk == "curtain.switch":
        val = state.get("on_off")
        return {"state": val.upper()}

    if spk == "hvac.ac":
        return {
            "mode": state.get("mode"),
            "temperature": state.get("set_temp")
        }

    return state