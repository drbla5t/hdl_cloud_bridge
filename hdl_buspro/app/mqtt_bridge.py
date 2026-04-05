import json
import paho.mqtt.client as mqtt


class MQTTBridge:
    def __init__(self, config, on_command):
        self.on_command = on_command
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        if config.MQTT_USER:
            self.client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)

        self.host = config.MQTT_HOST
        self.port = config.MQTT_PORT

    def connect(self):
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        print(f"MQTT connected: {reason_code}")
        client.subscribe("hdl/+/set")
        client.subscribe("hdl/+/mode/set")
        client.subscribe("hdl/+/temp/set")
        client.subscribe("hdl/+/fan/set")

    def _on_message(self, client, userdata, msg):
        payload_raw = msg.payload.decode().strip()
        if not payload_raw:
            return

        topic_parts = msg.topic.split("/")
        if len(topic_parts) < 3:
            return

        device_uid = topic_parts[1]
        action = topic_parts[2]

        if action == "set":
            payload = {"value": payload_raw, "_topic_action": "set"}
        elif action == "mode":
            payload = {"value": payload_raw, "_topic_action": "mode_set"}
        elif action == "temp":
            payload = {"value": payload_raw, "_topic_action": "temp_set"}
        elif action == "fan":
            payload = {"value": payload_raw, "_topic_action": "fan_mode_set"}
        else:
            try:
                payload = json.loads(payload_raw)
            except Exception:
                return

        print(f"CMD: {device_uid} {payload}")
        self.on_command(device_uid, payload)

    def publish(self, topic, payload, retain=False):
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload, ensure_ascii=False)
        else:
            payload = str(payload)

        self.client.publish(topic, payload, retain=retain)