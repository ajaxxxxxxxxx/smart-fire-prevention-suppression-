"""
Fusion server: combines IoT sensor data (via MQTT) with CNN camera predictions
to compute a fire-risk score and trigger prevention (alert) or suppression (pump).

Run:
    python server/fusion_server.py --model fire_model.keras --camera 0 --broker 192.168.1.100
"""
import argparse
import json
import time
import cv2
import numpy as np
import paho.mqtt.client as mqtt
import tensorflow as tf

NODE_ID = "node1"
state = {"temp": 25.0, "hum": 50.0, "gas": 0, "flame": False, "pump": False}

# ---- thresholds (tune for your hardware) ----
ALERT_RISK = 0.40       # prevention: warn / buzzer
SUPPRESS_RISK = 0.70    # suppression: start pump
CLEAR_RISK = 0.25       # stop pump when risk drops below this

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        state.update({k: data[k] for k in state if k in data})
    except Exception as e:
        print("Bad payload:", e)

def risk_score(cnn_prob):
    temp_s = np.clip((state["temp"] - 35) / 35, 0, 1)      # 35C -> 0, 70C -> 1
    gas_s = np.clip(state["gas"] / 4095, 0, 1)
    flame_s = 1.0 if state["flame"] else 0.0
    return float(0.45 * cnn_prob + 0.20 * temp_s + 0.15 * gas_s + 0.20 * flame_s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="fire_model.keras")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--broker", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    a = ap.parse_args()

    model = tf.keras.models.load_model(a.model)
    cap = cv2.VideoCapture(a.camera)

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(a.broker, a.port)
    client.subscribe(f"fire/{NODE_ID}/sensors")
    client.loop_start()
    cmd_topic = f"fire/{NODE_ID}/cmd"

    pump_active = False
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Camera read failed"); time.sleep(1); continue
        rgb = cv2.cvtColor(cv2.resize(frame, (224, 224)), cv2.COLOR_BGR2RGB)
        p = float(model.predict(rgb.astype("float32")[None, ...], verbose=0)[0][0])
        risk = risk_score(p)
        print(f"CNN={p:.2f} risk={risk:.2f} sensors={state}")

        if risk >= SUPPRESS_RISK and not pump_active:
            client.publish(cmd_topic, "PUMP_ON"); pump_active = True
            print(">>> SUPPRESSION: pump ON")
        elif risk >= ALERT_RISK and not pump_active:
            client.publish(cmd_topic, "ALERT")
            print(">>> PREVENTION: alert raised")
        elif risk < CLEAR_RISK:
            client.publish(cmd_topic, "CLEAR")
            if pump_active:
                client.publish(cmd_topic, "PUMP_OFF"); pump_active = False
                print(">>> Risk cleared: pump OFF")
        time.sleep(1)

if __name__ == "__main__":
    main()
