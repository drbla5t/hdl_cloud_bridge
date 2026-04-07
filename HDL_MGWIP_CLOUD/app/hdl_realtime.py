import json
import threading
import time

import paho.mqtt.client as mqtt

from app.hdl_crypto import decrypt_mqtt


class HDLRealtimeClient:
    def __init__(self, home_id, broker, client_id, username, password, on_event):
        self.home_id = str(home_id)
        self.broker = broker
        self.client_id = client_id
        self.username = username
        self.password = password
        self.on_event = on_event

        self.client = mqtt.Client(client_id=self.client_id)
        self.client.username_pw_set(self.username, self.password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        self._started = False
        self._lock = threading.Lock()

    def topics(self):
        home_id = self.home_id
        return [
            f"/user/{home_id}/app/thing/property/send",
            f"/user/{home_id}/app/thing/event/appHomeRefresh/up",
            f"/user/{home_id}/app/son/session/online",
            f"/user/{home_id}/app/thing/topo/found",
            f"/user/{home_id}/app/thing/event/intrude_alarm_event/up",
            f"/user/{home_id}/app/thing/event/tumble_alarm_event/up",
            f"/user/{home_id}/app/thing/event/stay_alarm_event/up",
            f"/user/{home_id}/app/thing/event/posture_calibration_event/up",
            f"/user/{home_id}/app/ota/device/progress/up",
        ]

    def start(self):
        with self._lock:
            if self._started:
                return
            self._started = True

        host, port = self._parse_broker(self.broker)
        print(f"HDL realtime connect: {host}:{port} home={self.home_id}")

        self.client.connect(host, port, 60)
        self.client.loop_start()

    def stop(self):
        with self._lock:
            if not self._started:
                return
            self._started = False

        try:
            self.client.loop_stop()
        except Exception:
            pass

        try:
            self.client.disconnect()
        except Exception:
            pass

    def _parse_broker(self, broker):
        broker = broker.strip()
        if "://" in broker:
            broker = broker.split("://", 1)[1]

        if "/" in broker:
            broker = broker.split("/", 1)[0]

        if ":" in broker:
            host, port = broker.rsplit(":", 1)
            return host, int(port)

        return broker, 1883

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        print(f"HDL realtime connected: rc={reason_code} home={self.home_id}")
        for topic in self.topics():
            client.subscribe(topic, qos=0)
            print(f"HDL realtime subscribed: {topic}")

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties=None):
        print(f"HDL realtime disconnected: rc={reason_code} home={self.home_id}")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        print(f"HDL realtime RX topic={topic}")

        if topic.endswith("/app/thing/event/appHomeRefresh/up"):
            self.on_event(self.home_id, topic, {"type": "home_refresh"})
            return

        try:
            decrypted = decrypt_mqtt(msg.payload, self.home_id)
            print(f"HDL realtime decrypted: {decrypted[:500]}")
        except Exception as e:
            print(f"HDL realtime decrypt failed topic={topic}: {e}")
            return

        try:
            data = json.loads(decrypted)
        except Exception as e:
            print(f"HDL realtime JSON parse failed topic={topic}: {e}")
            return

        self.on_event(self.home_id, topic, data)


class HDLRealtimeManager:
    def __init__(self, hdl_client, on_event):
        self.hdl = hdl_client
        self.on_event = on_event
        self.clients = {}

    def start_for_homes(self, homes):
        for home in homes:
            self.start_for_home(home)

    def start_for_home(self, home):
        home_id = str(home["homeId"])

        if home_id in self.clients:
            return

        attach_client_id = f"ha_{int(time.time())}_{home_id[-6:]}"
        mqtt_info = self.hdl.get_mqtt_info(
            home_id=home_id,
            attach_client_id=attach_client_id,
            home_type=home.get("homeType", "BUSPRO"),
            device_uuid="",
        )

        client = HDLRealtimeClient(
            home_id=home_id,
            broker=mqtt_info["url"],
            client_id=mqtt_info["clientId"],
            username=mqtt_info["userName"],
            password=mqtt_info["passWord"],
            on_event=self.on_event,
        )
        client.start()
        self.clients[home_id] = client

    def stop_all(self):
        for client in self.clients.values():
            client.stop()
        self.clients = {}