"""Quick test: classify a single image or run live on the webcam.
    python deep_learning/predict.py --model fire_model.keras --image test.jpg
    python deep_learning/predict.py --model fire_model.keras --camera 0
"""
import argparse
import cv2
import tensorflow as tf

def fire_probability(model, bgr_frame):
    rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
    x = cv2.resize(rgb, (224, 224)).astype("float32")[None, ...]
    return float(model.predict(x, verbose=0)[0][0])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="fire_model.keras")
    ap.add_argument("--image")
    ap.add_argument("--camera", type=int)
    a = ap.parse_args()
    model = tf.keras.models.load_model(a.model)

    if a.image:
        p = fire_probability(model, cv2.imread(a.image))
        print(f"Fire probability: {p:.2%}")
    elif a.camera is not None:
        cap = cv2.VideoCapture(a.camera)
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            p = fire_probability(model, frame)
            color = (0, 0, 255) if p > 0.5 else (0, 200, 0)
            cv2.putText(frame, f"Fire: {p:.0%}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.imshow("Fire detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()
