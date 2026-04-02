import time

from cloud_api import HdlCloudApi
from config_store import ConfigStore
from device_registry import DeviceRegistry
from mqtt_bridge import LocalMqttBridge
from project_context import ProjectContext


class App:
    def __init__(self):
        cfg = ConfigStore("config.json").load()

        self.state_refresh_sec = int(cfg.get("polling", {}).get("state_refresh_sec", 15))

        self.ctx = ProjectContext(
            project_id=str(cfg["hdl"]["project_id"]),
            project_name="HDL Project",
            home_id=int(cfg["hdl"]["home_id"]),
        )

        self.api = HdlCloudApi(
            base_url=cfg["hdl"]["base_url"],
            app_key=cfg["hdl"]["app_key"],
            app_secret=cfg["hdl"]["app_secret"],
            home_id=self.ctx.home_id,
        )

        self.registry = DeviceRegistry()

        self.bridge = LocalMqttBridge(
            host=cfg["mqtt"]["host"],
            port=int(cfg["mqtt"]["port"]),
            username=cfg["mqtt"]["username"],
            password=cfg["mqtt"]["password"],
            on_switch_command=self.handle_switch_command,
        )

    def bootstrap(self):
        projects = self.api.get_projects()
        selected = next((p for p in projects if p.project_id == self.ctx.project_id), None)
        if not selected:
            raise RuntimeError(f"Configured project_id not found: {self.ctx.project_id}")

        self.ctx.project_name = selected.name
        print("Using project:", self.ctx.project_name, self.ctx.project_id)

        devices = self.api.get_devices_by_project(self.ctx.project_id)
        print(f"Found {len(devices)} device(s)")

        self.registry.replace(devices)

        for dev in self.registry.all():
            print(dev.device_iot_id, dev.spk, dev.status)
            if dev.spk == "light.switch":
                self.bridge.publish_switch_discovery(dev)
                self.bridge.publish_state(dev)

    def refresh_states(self):
        devices = self.api.get_devices_by_project(self.ctx.project_id)
        self.registry.replace(devices)

        for dev in self.registry.all():
            if dev.spk == "light.switch":
                self.bridge.publish_state(dev)

    def handle_switch_command(self, device_id: str, state: str):
        device = self.registry.get(device_id)
        if not device:
            print(f"Unknown device: {device_id}")
            return

        result = self.api.control_switch(device, state)
        print("CONTROL RESULT:", result)

        time.sleep(1)
        self.refresh_states()

    def run(self):
        self.bootstrap()
        self.bridge.loop_start()

        try:
            while True:
                self.refresh_states()
                time.sleep(self.state_refresh_sec)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.bridge.loop_stop()
            self.bridge.disconnect()


if __name__ == "__main__":
    App().run()