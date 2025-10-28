"""
Generate synthetic aggregated road-segment features and train a RandomForest classifier.
Saves model to model.pkl in the same folder (used by model_server & stream_processor).
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump
import os
from datetime import datetime, timedelta
import random

OUT_MODEL = "/app/model.pkl"

def generate_dataset(n_segments=200, days=7):
    rows = []
    start = datetime(2025,1,1,0,0)
    for seg_id in range(n_segments): # for each road segment in a road
        base_speed = 40 - (seg_id % 10)  # variability per road
        for minute in range(days * 24 * 60): # for each minute in 7 days 
            # create one data row for avg speed & vehicle count
            ts = start + timedelta(minutes=minute)
            hour = ts.hour

            # Stimulating rush hour traffic 
            rush = 15 if 7 <= hour <= 9 or 17 <= hour <= 19 else 0 
            avg_speed = max(3, np.random.normal(base_speed - rush, 6.0))
            vehicle_count = max(0, int(np.random.normal(20 if rush else 8, 6)))
            # binary congestion label: avg_speed < 0.5 * (speed_limit ~ 50)
            label = 1 if avg_speed < 25 else 0
            rows.append({
                "road_segment_id": f"R{seg_id}",
                "ts": ts,
                "avg_speed": avg_speed,
                "vehicle_count": vehicle_count,
                "hour": hour,
                "dayofweek": ts.weekday(),
                "label": label
            })
    return pd.DataFrame(rows)

def train_and_save():
    print("Generating synthetic dataset (this may take a moment)...")
    
    # Simulates 500 road segments for 20 days --> millions of data points
    df = generate_dataset(n_segments=500, days=20)  # smaller for speed
    features = ["avg_speed", "vehicle_count", "hour", "dayofweek"]

    X = df[features]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    
    print(f"Trained RandomForest. Test accuracy: {acc:.3f}")
    dump(model, OUT_MODEL)
    print(f"Saved model to {OUT_MODEL}")

if __name__ == "__main__":
    train_and_save()
