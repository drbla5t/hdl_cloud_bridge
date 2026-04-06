# 🏠 HDL Buspro Bridge (Cloud → MQTT → Home Assistant)

![HA Add-on](https://img.shields.io/badge/Home%20Assistant-Add--on-blue)
![MQTT](https://img.shields.io/badge/MQTT-supported-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

Bridge between **HDL Buspro Cloud API** and **Home Assistant via MQTT**.

Supports:
- 💡 Lights (switch / dimming / CCT / RGBW)
- 🪟 Curtains
- 🌡 Climate (AC, floor heating)
- 📡 Real-time state sync (polling)
- ⚡ Instant update after command

---

## ⚠️ Disclaimer

This project is **not affiliated with HDL Automation**.  
It uses reverse-engineered Cloud API.

Use at your own risk.

---

## 🚀 Features

- Auto-discovery in Home Assistant (MQTT Discovery)
- Supports multiple homes
- Works via HDL Cloud (no local gateway required)
- Fast state updates after control
- Extensible device registry (easy to add new types)

---

## 📦 Installation (Home Assistant Add-on)

1. Add this repository to Home Assistant:
Settings → Add-ons → Add-on Store → ⋮ → Repositories
2. Install **HDL Buspro Bridge**

3. Configure:

```yaml
hdl_user: your@yandex.ru
hdl_pass: your_password
hdl_server: ru
mqtt_host: core-mosquitto
mqtt_port: 1883
mqtt_user: ""
mqtt_pass: ""
poll_interval: 10
home_names:
  - your_home_name
```

hdl_server names:
ru - Russia
bahrain - Bahrain
china - China

4.	Start the add-on

## ☕ Support the project

<p align="center">
  <img src="assets/qrCode.png" width="220"><br><br>
  <b>Scan QR to support development</b><br>
  Your support helps improve the HDL Buspro integration 🙌
</p>