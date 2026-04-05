import json
import time

from app import config
from app.hdl_api import HDLClient
from app.mqtt_bridge import MQTTBridge
from app.discovery import Discovery
from app.command_router import CommandRouter
from app.home_selector import select_homes
from app.state_publisher import StatePublisher



class App:
    def __init__(self):
        self.hdl = HDLClient(config.USERNAME, config.PASSWORD)
        self.mqtt = MQTTBridge(config, self.handle_command)
        self.discovery = Discovery(self.mqtt)
        self.state_publisher = StatePublisher(self.mqtt)
        self.command_router = CommandRouter()

        self.selected_homes = []
        self.device_index = {}

    def rebuild_device_index(self):
        self.device_index = {}

        for home in self.selected_homes:
            home_id = home["homeId"]
            home_name = home["homeName"]

            devices = self.hdl.get_devices(home_id)

            for d in devices:
                uid = d.get("deviceIotId") or d.get("deviceId")
                if not uid:
                    continue

                d["_home_id"] = home_id
                d["_home_name"] = home_name
                self.device_index[uid] = d

    def handle_command(self, device_uid, payload):
        device = self.device_index.get(device_uid)
        if not device:
            print(f"Device not found: {device_uid}")
            return

        cmd = self.command_router.handle(device, payload)
        if not cmd:
            return

        print(
            f"HDL TX home={device['_home_name']} "
            f"gateway={device['gatewayId']} "
            f"deviceId={device['deviceId']} "
            f"spk={device['spk']} "
            f"key={cmd['key']} value={cmd['value']}"
        )

        self.hdl.control(
            home_id=device["_home_id"],
            gateway_id=device["gatewayId"],
            device=device,
            key=cmd["key"],
            value=cmd["value"],
        )


    def publish_discovery(self):
        for device in self.device_index.values():
            self.discovery.publish(device)

    def publish_states(self):
        for device in self.device_index.values():
            self.state_publisher.publish(device)

    def start(self):
        self.hdl.login()

        all_homes = self.hdl.get_homes()
        self.selected_homes = select_homes(all_homes, config.HDL_HOME_NAMES)

        print("Selected homes:")
        for h in self.selected_homes:
            print(f'- {h["homeName"]} ({h["homeId"]})')

        self.rebuild_device_index()

        self.mqtt.connect()
        self.publish_discovery()
        self.publish_states()

        while True:
            self.rebuild_device_index()
            self.publish_states()
            time.sleep(config.POLL_INTERVAL)


def run():
    app = App()
    app.start()