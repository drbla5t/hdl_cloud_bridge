def build(device):
    uid = device.get("deviceIotId") or device.get("deviceId")
    name = device.get("name", uid)
    spk = device.get("spk", "")

    if spk == "hvac.floorHeat":
        return {
            "topic": f"homeassistant/climate/hdl_{uid}/config",
            "payload": {
                "name": name,
                "unique_id": f"hdl_{uid}",
                "mode_command_topic": f"hdl/{uid}/mode/set",
                "mode_state_topic": f"hdl/{uid}/state",
                "mode_state_template": "{{ value_json.mode }}",
                "temperature_command_topic": f"hdl/{uid}/temp/set",
                "temperature_state_topic": f"hdl/{uid}/state",
                "temperature_state_template": "{{ value_json.temperature }}",
                "current_temperature_topic": f"hdl/{uid}/state",
                "current_temperature_template": "{{ value_json.current_temperature }}",
                "preset_mode_command_topic": f"hdl/{uid}/preset_mode/set",
                "preset_mode_state_topic": f"hdl/{uid}/state",
                "preset_mode_value_template": "{{ value_json.preset_mode }}",
                "availability_topic": f"hdl/{uid}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "modes": ["off", "heat", "cool", "eco"],
                "preset_modes": ["day", "night", "away", "normal", "timer"],
                "min_temp": 16,
                "max_temp": 35,
                "temp_step": 1,
            },
        }

    return {
        "topic": f"homeassistant/climate/hdl_{uid}/config",
        "payload": {
            "name": name,
            "unique_id": f"hdl_{uid}",
            "mode_command_topic": f"hdl/{uid}/mode/set",
            "mode_state_topic": f"hdl/{uid}/state",
            "mode_state_template": "{{ value_json.mode }}",
            "temperature_command_topic": f"hdl/{uid}/temp/set",
            "temperature_state_topic": f"hdl/{uid}/state",
            "temperature_state_template": "{{ value_json.temperature }}",
            "current_temperature_topic": f"hdl/{uid}/state",
            "current_temperature_template": "{{ value_json.current_temperature }}",
            "fan_mode_command_topic": f"hdl/{uid}/fan/set",
            "fan_mode_state_topic": f"hdl/{uid}/state",
            "fan_mode_value_template": "{{ value_json.fan_mode }}",
            "swing_mode_command_topic": f"hdl/{uid}/swing/set",
            "swing_mode_state_topic": f"hdl/{uid}/state",
            "swing_mode_value_template": "{{ value_json.swing_mode }}",
            "availability_topic": f"hdl/{uid}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "modes": ["off", "cool", "heat", "dry", "fan_only", "auto"],
            "fan_modes": ["low", "medium", "high", "auto"],
            "swing_modes": ["off", "vertical", "horizontal"],
            "min_temp": 16,
            "max_temp": 30,
            "temp_step": 1,
        },
    }
1