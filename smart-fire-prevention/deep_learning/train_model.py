"""
Train a fire / no-fire image classifier using MobileNetV2 transfer learning.

Dataset layout:
    dataset/
        train/fire/*.jpg      dataset/train/no_fire/*.jpg
        val/fire/*.jpg        dataset/val/no_fire/*.jpg

Usage:
    python deep_learning/train_model.py --data dataset --epochs 10
"""
import argparse
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from sklearn.metrics import classification_report, confusion_matrix

IMG_SIZE = (224, 224)

def build_model():
    base = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights="imagenet")
    base.trainable = False
    model = models.Sequential([
        layers.Input(shape=IMG_SIZE + (3,)),
        layers.Rescaling(1.0 / 127.5, offset=-1),
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        base,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(1, activation="sigmoid"),   # P(fire)
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="dataset")
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--out", default="fire_model.keras")
    a = p.parse_args()

    # Folder names are sorted alphabetically: fire=0, no_fire=1.
    # We flip labels below so that fire = 1 (positive class).
    train = tf.keras.utils.image_dataset_from_directory(
        f"{a.data}/train", image_size=IMG_SIZE, batch_size=a.batch, label_mode="binary")
    val = tf.keras.utils.image_dataset_from_directory(
        f"{a.data}/val", image_size=IMG_SIZE, batch_size=a.batch, label_mode="binary", shuffle=False)
    flip = lambda x, y: (x, 1.0 - y)
    train = train.map(flip).prefetch(tf.data.AUTOTUNE)
    val = val.map(flip).prefetch(tf.data.AUTOTUNE)

    model = build_model()
    model.fit(train, validation_data=val, epochs=a.epochs)
    model.save(a.out)
    print(f"Model saved to {a.out}")

    y_true, y_pred = [], []
    for x, y in val:
        y_true.extend(y.numpy().ravel())
        y_pred.extend((model.predict(x, verbose=0).ravel() > 0.5).astype(int))
    print(confusion_matrix(y_true, y_pred))
    print(classification_report(y_true, y_pred, target_names=["no_fire", "fire"]))

if __name__ == "__main__":
    main()
