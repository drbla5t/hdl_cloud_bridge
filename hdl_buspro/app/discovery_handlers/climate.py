def build(uid, name):
    return {
        "topic": f"homeassistant/climate/hdl_{uid}/config",
        "payload": {
            "name": name,
            "unique_id": f"hdl_{uid}",
            "mode_command_topic": f"hdl/{uid}/mode/set",
            "mode_state_topic": f"hdl/{uid}/mode/state",
            "temperature_command_topic": f"hdl/{uid}/temp/set",
            "temperature_state_topic": f"hdl/{uid}/temp/state",
            "current_temperature_topic": f"hdl/{uid}/current_temp/state",
            "fan_mode_command_topic": f"hdl/{uid}/fan/set",
            "fan_mode_state_topic": f"hdl/{uid}/fan/state",
            "availability_topic": f"hdl/{uid}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "modes": ["off", "cool", "heat", "dry", "fan_only", "auto"],
            "fan_modes": ["low", "medium", "high", "auto"],
            "min_temp": 16,
            "max_temp": 30,
            "temp_step": 1,
        },
    }