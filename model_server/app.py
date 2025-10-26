from fastapi import FastAPI
import redis, os, json
from joblib import load
from pydantic import BaseModel
import typing as t
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

MODEL_PATH = "/app/../trainer/model.pkl"
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "/app/model.pkl"

model = None
try:
    model = load(MODEL_PATH)
    print("Loaded model at", MODEL_PATH)
except Exception as e:
    print("Model load failed:", e)
    model = None

class FeaturePayload(BaseModel):
    avg_speed: float
    vehicle_count: int
    hour: int
    dayofweek: int

@app.get("/segments/latest")
def latest_segments(limit: int = 200):
    keys = r.keys("segment:*")
    out = []
    for k in keys[:limit]:
        h = r.hgetall(k)
        if h:
            out.append(h)
    return {"count": len(out), "segments": out}

@app.post("/predict")
def predict(payload: FeaturePayload):
    features = [payload.avg_speed, payload.vehicle_count, payload.hour, payload.dayofweek]
    if model is None:
        prob = 1.0 if payload.avg_speed < 25 else 0.0
    else:
        prob = float(model.predict_proba([features])[0][1])
    return {"congestion_prob": prob}
