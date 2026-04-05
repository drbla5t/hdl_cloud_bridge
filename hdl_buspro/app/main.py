import time
import os

from app.hdl_api import HDLClient
from app.mqtt_bridge import MQTTBridge
from app.discovery import Discovery
from app.state_publisher import StatePublisher
from app.command_router import CommandRouter
from app.home_selector import HomeSelector
import app.config as config


class App:
    def __init__(self):
        self.hdl = HDLClient(
            os.getenv("HDL_USER"),
            os.getenv("HDL_PASS"),
        )

        self.mqtt = MQTTBridge(self, self.handle_command)
        self.discovery = Discovery(self.mqtt)
        self.state = StatePublisher(self.mqtt)
        self.router = CommandRouter()

        self.homes = []

    def handle_command(self, device_id, payload):
        device = next(
            (d for d in self.devices if d.get("deviceIotId") == device_id),
            None,
        )

        if not device:
            print("Device not found:", device_id)
            return

        cmd = self.router.handle(device, payload)
        if not cmd:
            return

        self.hdl.control(
            home_id=self.home["homeId"],
            gateway_id=device["gatewayId"],
            device_id=device["deviceId"],
            key=cmd["key"],
            value=cmd["value"],
        )

    def start(self):
        print("🔐 Login...")
        self.hdl.login()

        selector = HomeSelector(self.hdl, config.HDL_HOME_NAMES)
        self.homes = selector.select()

        print("Selected home:", self.home["homeName"])

        self.mqtt.connect()

        while True:
            self.devices = []

            for home in self.homes:
                devices = self.hdl.get_devices(home["homeId"])

                for d in devices:
                    d["_home_name"] = home["homeName"]

                self.devices.extend(devices)

                self.discovery.publish(d)
                self.state.publish(d)

            time.sleep(int(os.getenv("POLL_INTERVAL", 5)))


def run():
    App().start()


if __name__ == "__main__":
    run()