import json
from typing import Callable

import paho.mqtt.client as mqtt

from models import DeviceInfo


class LocalMqttBridge:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        on_switch_command: Callable[[str, str], None],
    ):
        self.on_switch_command = on_switch_command
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if username:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(host, port, 60)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        print("Connected to local MQTT")
        client.subscribe("hdlcloud/set/#")
        print("Subscribed to hdlcloud/set/#")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode().strip()

        print("MQTT CMD:", topic, payload)

        if topic.startswith("hdlcloud/set/"):
            device_id = topic.split("/")[-1]
            self.on_switch_command(device_id, payload)

    def publish_switch_discovery(self, dev: DeviceInfo):
        name = dev.name or "Реле"
        topic = f"homeassistant/switch/{dev.device_iot_id}/config"

        payload = {
            "name": name,
            "unique_id": f"hdlcloud_{dev.device_iot_id}",
            "state_topic": f"hdlcloud/state/{dev.device_iot_id}",
            "command_topic": f"hdlcloud/set/{dev.device_iot_id}",
            "value_template": "{{ value_json.on_off }}",
            "payload_on": "on",
            "payload_off": "off",
            "state_on": "on",
            "state_off": "off",
            "device": {
                "identifiers": [f"hdlcloud_{dev.device_iot_id}"],
                "name": name,
                "manufacturer": "HDL",
                "model": dev.model or "HDL"
            }
        }

        self.client.publish(topic, json.dumps(payload, ensure_ascii=False), retain=True)

    def publish_state(self, dev: DeviceInfo):
        status = {}
        for item in dev.status or []:
            status[item["key"]] = item["value"]

        status["online"] = dev.online
        status["spk"] = dev.spk
        status["sid"] = dev.sid

        self.client.publish(
            f"hdlcloud/state/{dev.device_iot_id}",
            json.dumps(status, ensure_ascii=False),
            retain=True,
        )

    def loop_start(self):
        self.client.loop_start()

    def loop_stop(self):
        self.client.loop_stop()

    def disconnect(self):
        self.client.disconnect()