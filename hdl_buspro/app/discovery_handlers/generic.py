def build(device):
    uid = device.get("deviceIotId") or device.get("deviceId")
    name = device.get("name", uid)

    return {
        "topic": f"homeassistant/switch/hdl_{uid}/config",
        "payload": {
            "name": name,
            "unique_id": f"hdl_{uid}",
            "state_topic": f"hdl/{uid}/state",
            "command_topic": f"hdl/{uid}/set",
            "payload_on": "ON",
            "payload_off": "OFF",
            "state_on": "ON",
            "state_off": "OFF",
            "availability_topic": f"hdl/{uid}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
    }
1