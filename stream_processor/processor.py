import os, json, time
from kafka import KafkaConsumer
from collections import deque, defaultdict
from datetime import datetime, timezone, timedelta
import redis
from joblib import load
import pandas as pd

KAFKA = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
TOPIC = "gps.pings"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    consumer_timeout_ms=10000,
    api_version=(0, 10)  # ✅ Important fix
)


r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# Load model (trainer should have produced model.pkl)
MODEL_PATH = "/app/../trainer/model.pkl"  # docker-compose keeps folders next to each other
if not os.path.exists(MODEL_PATH):
    # try /app/model.pkl if user placed it
    MODEL_PATH = "/app/model.pkl"
model = None
try:
    model = load(MODEL_PATH)
    print("Loaded model from", MODEL_PATH)
except Exception as e:
    print("Could not load model:", e)
    model = None

# in-memory sliding windows per segment (deque of (timestamp, speed))
WINDOW_MINUTES = 5
buffers = defaultdict(lambda: deque())

def latlon_to_segment(lat, lon):
    # very simple grid-based segment id (for PoC). Real: map-matching to OSM road ID.
    lat_r = round(lat, 3)
    lon_r = round(lon, 3)
    return f"S_{lat_r}_{lon_r}"

def update_buffer(seg, ts, speed):
    dq = buffers[seg]
    dq.append((ts, speed))
    cutoff = ts - timedelta(minutes=WINDOW_MINUTES)
    while dq and dq[0][0] < cutoff:
        dq.popleft()

def compute_features(seg):
    dq = buffers[seg]
    if not dq:
        return None
    speeds = [s for (_t, s) in dq]
    avg_speed = float(pd.Series(speeds).mean())
    vehicle_count = len(speeds)
    now = datetime.now(timezone.utc)
    hour = now.hour
    dayofweek = now.weekday()
    return {"avg_speed": avg_speed, "vehicle_count": vehicle_count, "hour": hour, "dayofweek": dayofweek}

def store_prediction(seg, payload):
    # store JSON under Redis hash key "segment:{seg}"
    key = f"segment:{seg}"
    r.hset(key, mapping={
        "road_segment_id": seg,
        "ts": payload.get("ts"),
        "avg_speed": payload.get("avg_speed"),
        "vehicle_count": payload.get("vehicle_count"),
        "congestion_prob": payload.get("congestion_prob")
    })
    # also keep a small TTL
    r.expire(key, 60*60)  # 1 hour

def predict_prob(features):
    if model is None:
        # fallback rule if model isn't available
        return 1.0 if features["avg_speed"] < 25 else 0.0
    import numpy as np
    X = [[features["avg_speed"], features["vehicle_count"], features["hour"], features["dayofweek"]]]
    prob = model.predict_proba(X)[0][1]
    return float(prob)

def main_loop():
    print("Starting consumer loop, reading from", KAFKA)
    while True:
        for msg in consumer:
            try:
                v = msg.value
                ts = datetime.fromisoformat(v["timestamp"].replace("Z","+00:00"))
                seg = latlon_to_segment(v["lat"], v["lon"])
                update_buffer(seg, ts, v["speed_kmph"])
                feats = compute_features(seg)
                if feats is None:
                    continue
                prob = predict_prob(feats)
                payload = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "avg_speed": round(feats["avg_speed"],2),
                    "vehicle_count": feats["vehicle_count"],
                    "congestion_prob": round(prob,3)
                }
                store_prediction(seg, payload)
            except Exception as e:
                print("Error processing message:", e)
        # short sleep to avoid tight loop when consumer_timeout reached
        time.sleep(0.5)

if __name__ == "__main__":
    main_loop()
