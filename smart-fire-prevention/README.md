# 🔥 Smart Fire Prevention and Suppression using IoT and Deep Learning

An intelligent fire-safety system that **detects fire early** (prevention) and
**automatically extinguishes it** (suppression) by fusing IoT sensor readings with
a deep-learning image classifier.

## ✨ Features
- Real-time monitoring of temperature, humidity, smoke/gas and flame via ESP32
- CNN (MobileNetV2) detects fire from camera frames
- Sensor + vision **fusion** produces a fire-risk score, reducing false alarms
- Two-stage response: **alert** at medium risk, **pump activation** at high risk
- Local **fail-safe** on the ESP32 if network/server fails
- MQTT-based, easily extensible to multiple nodes and dashboards

## 🏗️ System Architecture
```
 [DHT22][MQ-2][Flame]                 [Camera]
        |                                 |
     ESP32 --MQTT--> Broker <--MQTT-- Fusion Server (Python + CNN)
        ^                                 |
        +---- PUMP_ON / ALERT commands ---+
        |
   Relay -> Water pump / Buzzer
```

## 📁 Repository Structure
```
├── firmware/esp32_fire_node/   # Arduino code for ESP32
├── deep_learning/              # Training + inference scripts
├── server/                     # MQTT + CNN fusion/decision server
├── docs/                       # Hardware wiring & MQTT reference
├── requirements.txt
└── README.md
```

## 🧰 Hardware
ESP32 DevKit, DHT22, MQ-2, flame sensor, relay module, mini water pump, buzzer,
USB/IP camera, 5V power supply. See [docs/HARDWARE.md](docs/HARDWARE.md).

## 🚀 Getting Started

### 1. Install dependencies
```bash
git clone https://github.com/<your-username>/smart-fire-prevention.git
cd smart-fire-prevention
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Train the model
Download a fire dataset (e.g., from Kaggle: "Fire Detection Dataset") and arrange it:
```
dataset/train/{fire,no_fire}   dataset/val/{fire,no_fire}
```
```bash
python deep_learning/train_model.py --data dataset --epochs 10
python deep_learning/predict.py --model fire_model.keras --image test.jpg
```

### 3. Flash the ESP32
Open `firmware/esp32_fire_node/esp32_fire_node.ino` in Arduino IDE, install
**PubSubClient**, **DHT sensor library**, **ArduinoJson**, set WiFi/MQTT details, upload.

### 4. Start the MQTT broker and fusion server
```bash
sudo apt install mosquitto && sudo systemctl start mosquitto
python server/fusion_server.py --model fire_model.keras --camera 0 --broker localhost
```

## ⚙️ How the Decision Logic Works
`risk = 0.45·CNN + 0.20·temperature + 0.15·gas + 0.20·flame`

| Risk        | Action                       |
|-------------|------------------------------|
| ≥ 0.40      | Prevention: buzzer / alert   |
| ≥ 0.70      | Suppression: pump ON         |
| < 0.25      | Clear alert, pump OFF        |

Thresholds can be tuned at the top of `server/fusion_server.py`.

## 📊 Results
> Replace with your own numbers.

| Metric    | Value |
|-----------|-------|
| Accuracy  | XX %  |
| Precision | XX %  |
| Recall    | XX %  |
| Response time | X s |

Add screenshots / circuit photos / demo video link here.

## 🔮 Future Work
- Cloud dashboard (Grafana / Blynk), SMS/Telegram alerts
- Edge deployment with TensorFlow Lite on Raspberry Pi
- Smoke detection and multi-camera support
- Multi-node deployment across rooms

## ⚠️ Disclaimer
Academic prototype. Not a certified fire-safety device.

## 📜 License
MIT – see [LICENSE](LICENSE).

## 👤 Author
**Your Name** – [GitHub](https://github.com/your-username) · [LinkedIn](https://linkedin.com/in/your-profile)
