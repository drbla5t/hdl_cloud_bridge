import time

from app import config
from app.hdl_api import HDLClient
from app.mqtt_bridge import MQTTBridge
from app.discovery import Discovery
from app.command_router import CommandRouter
from app.home_selector import select_homes
from app.state_publisher import StatePublisher
from app.hdl_realtime import HDLRealtimeManager


class App:
    def __init__(self):
        self.hdl = HDLClient(
            config.USERNAME,
            config.PASSWORD,
            config.HDL_SERVERS,
            config.HDL_SERVER,
        )
        self.mqtt = MQTTBridge(config, self.handle_command)
        self.discovery = Discovery(self.mqtt)
        self.state_publisher = StatePublisher(self.mqtt)
        self.command_router = CommandRouter()
        self.realtime = HDLRealtimeManager(self.hdl, self.handle_realtime_event)

        self.selected_homes = []
        self.device_index = {}
        self.sid_index = {}

    def rebuild_device_index(self):
        self.device_index = {}
        self.sid_index = {}

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

                sid = d.get("sid")
                if sid:
                    self.sid_index[sid] = d

    def refresh_home_devices(self, home_id):
        target_home = None
        for home in self.selected_homes:
            if home["homeId"] == home_id:
                target_home = home
                break

        if not target_home:
            return

        home_name = target_home["homeName"]
        devices = self.hdl.get_devices(home_id)

        to_delete = [
            uid for uid, d in self.device_index.items()
            if d.get("_home_id") == home_id
        ]
        for uid in to_delete:
            dev = self.device_index.pop(uid, None)
            if dev and dev.get("sid") in self.sid_index:
                self.sid_index.pop(dev.get("sid"), None)

        for d in devices:
            uid = d.get("deviceIotId") or d.get("deviceId")
            if not uid:
                continue

            d["_home_id"] = home_id
            d["_home_name"] = home_name
            self.device_index[uid] = d

            sid = d.get("sid")
            if sid:
                self.sid_index[sid] = d

    def handle_command(self, device_uid, payload):
        device = self.device_index.get(device_uid)
        if not device:
            print(f"Device not found: {device_uid}")
            return

        cmd = self.command_router.handle(device, payload)
        if not cmd:
            return

        if isinstance(cmd, list):
            attrs = cmd
        else:
            attrs = [cmd]

        print(
            f"HDL TX home={device['_home_name']} "
            f"gateway={device['gatewayId']} "
            f"deviceId={device['deviceId']} "
            f"spk={device['spk']} "
            f"attrs={attrs}"
        )

        try:
            self.hdl.control(
                home_id=device["_home_id"],
                gateway_id=device["gatewayId"],
                device=device,
                attrs=attrs,
            )

        except Exception as e:
            print(f"Command send failed: {e}")

    def publish_discovery(self):
        for device in self.device_index.values():
            self.discovery.publish(device)

    def publish_states(self):
        for device in self.device_index.values():
            self.state_publisher.publish(device)

    def publish_device_state(self, device):
        self.state_publisher.publish(device)

    def initial_load(self):
        self.hdl.login()

        all_homes = self.hdl.get_homes()
        self.selected_homes = select_homes(all_homes, config.HDL_HOME_NAMES)

        print("Selected homes:")
        for h in self.selected_homes:
            print(f'- {h["homeName"]} ({h["homeId"]})')

        self.rebuild_device_index()

    def _status_list_to_dict(self, status_items):
        result = {}
        if not isinstance(status_items, list):
            return result

        for item in status_items:
            if not isinstance(item, dict):
                continue
            key = item.get("key")
            if key is None:
                continue
            result[key] = item.get("value")
        return result

    def _merge_status(self, device, new_status_items):
        if not isinstance(new_status_items, list):
            return False

        current_list = device.get("status") or []
        current_map = self._status_list_to_dict(current_list)
        changed = False

        for item in new_status_items:
            if not isinstance(item, dict):
                continue

            key = item.get("key")
            value = item.get("value")

            if key is None:
                continue

            if current_map.get(key) != value:
                current_map[key] = value
                changed = True

        if changed:
            device["status"] = [
                {"key": k, "value": v}
                for k, v in current_map.items()
            ]

        return changed

    def _set_online_by_sid(self, sid, online_value):
        device = self.sid_index.get(sid)
        if not device:
            return

        old = bool(device.get("online"))
        new = bool(online_value)

        if old != new:
            device["online"] = new
            self.publish_device_state(device)

    def handle_realtime_event(self, home_id, topic, data):
        try:
            if not isinstance(data, dict):
                return

            if data.get("type") == "home_refresh":
                print(f"HDL realtime refresh requested for home={home_id}")
                self.refresh_home_devices(home_id)
                self.publish_states()
                return

            objects = data.get("objects") or []

            if topic.endswith("/app/son/session/online"):
                for obj in objects:
                    sid = obj.get("sid")
                    if not sid:
                        continue

                    raw_online = (
                        obj.get("online")
                        or obj.get("isOnline")
                        or obj.get("value")
                        or obj.get("status")
                    )

                    online = str(raw_online).lower() in ("1", "true", "online", "on")
                    self._set_online_by_sid(sid, online)
                return

            if topic.endswith("/app/thing/property/send"):
                for obj in objects:
                    sid = obj.get("sid")
                    if not sid:
                        continue

                    device = self.sid_index.get(sid)
                    if not device:
                        continue

                    status_items = obj.get("status") or []
                    if self._merge_status(device, status_items):
                        self.publish_device_state(device)
                return

            # для остальных realtime событий пока просто мягкий refresh дома
            print(f"HDL realtime other topic -> refresh home: {topic}")
            self.refresh_home_devices(home_id)
            self.publish_states()

        except Exception as e:
            print(f"Realtime event handle error: {e}")

    def start(self):
        self.initial_load()

        self.mqtt.connect()
        self.publish_discovery()
        self.publish_states()

        try:
            self.realtime.start_for_homes(self.selected_homes)
        except Exception as e:
            print(f"Realtime start error: {e}")

        while True:
            try:
                self.rebuild_device_index()
                self.publish_states()
            except Exception as e:
                print(f"Fallback sync error: {e}")
                try:
                    print("Trying to relogin...")
                    self.hdl.login()
                except Exception as login_error:
                    print(f"Relogin failed: {login_error}")

            time.sleep(config.POLL_INTERVAL)


def run():
    app = App()
    app.start()


if __name__ == "__main__":
    run()