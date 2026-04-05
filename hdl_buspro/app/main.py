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

        self.mqtt = MQTTBridge(config, self.handle_command)
        self.discovery = Discovery(self.mqtt)
        self.state = StatePublisher(self.mqtt)
        self.router = CommandRouter()
        self.discovery_sent = set()

        self.homes = []

    def handle_command(self, device_uid, payload):
        
        devices = getattr(self, "devices", [])

        device = next(
            (
                d for d in devices
                if d.get("deviceIotId") == device_uid or d.get("deviceId") == device_uid
            ),
            None,
        )

        if not device:
            print(f"Device not found for command: {device_uid}")
            return

        cmd = self.router.handle(device, payload)
        if not cmd:
            return
        
        print(f"CMD → {device['name']} ({device_uid}) → {cmd}")
        
        self.hdl.control(
            device["homeId"],
            device["gatewayId"],
            device,
            cmd["key"],
            cmd["value"],
        )

    def start(self):
        print("🔐 Login...")
        self.hdl.login()

        selector = HomeSelector(self.hdl, config.HDL_HOME_NAMES)
        self.homes = selector.select()

        print("Selected homes:")
        for h in self.homes:
            print(f" - {h['homeName']} ({h['homeId']})")

        self.mqtt.connect()

        while True:
            self.devices = []

            for home in self.homes:
                try:
                    devices = self.hdl.get_devices(home["homeId"])

                    for d in devices:
                        d["_home_name"] = home["homeName"]
                        d["_home_id"] = home["homeId"]

                        self.devices.append(d)
                        self.discovery.publish(d)
                        self.state.publish(d)

                except Exception as e:
                    print(f"Failed to sync home {home['homeName']}: {e}")

            time.sleep(int(os.getenv("POLL_INTERVAL", 5)))


def run():
    App().start()


if __name__ == "__main__":
    run()