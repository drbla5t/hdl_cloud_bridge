def build(uid, name):
    return {
        "topic": f"homeassistant/cover/hdl_{uid}/config",
        "payload": {
            "name": name,
            "unique_id": f"hdl_{uid}",
            "command_topic": f"hdl/{uid}/set",
            "state_topic": f"hdl/{uid}/state",
            "payload_open": "OPEN",
            "payload_close": "CLOSE",
            "payload_stop": "STOP",
            "state_open": "OPEN",
            "state_closed": "CLOSED",
            "state_stopped": "STOPPED",
            "availability_topic": f"hdl/{uid}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
    }