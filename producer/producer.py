"""
Simple GPS simulator that produces JSON pings to Kafka topic 'gps.pings'.
"""
import json, time, random
from datetime import datetime, timezone
from kafka import KafkaProducer
import os

KAFKA = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = "gps.pings"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA],
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    retries=5,
    acks='all',
    api_version=(0, 10)  # ✅ Important fix
)


def generate_ping(vehicle_id, base_lat, base_lon):
    lat = base_lat + random.uniform(-0.01, 0.01)
    lon = base_lon + random.uniform(-0.01, 0.01)
    speed = max(0.0, random.gauss(30, 12))  # kmph
    return {
        "vehicle_id": vehicle_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lat": lat,
        "lon": lon,
        "speed_kmph": round(speed, 2),
        "source": "sim"
    }

def main():
    # create N vehicles in area roughly around a city centre lat/lon
    vehicles = []
    centers = [
        (12.9716, 77.5946), # sample center (Bengaluru)
        (12.9610, 77.5800),
        (12.9850, 77.6000)
    ]
    for i in range(100):
        c = centers[i % len(centers)]
        vehicles.append((f"veh_{i}", c[0] + random.uniform(-0.02,0.02), c[1] + random.uniform(-0.02,0.02)))

    print(f"Producing to {KAFKA} topic {TOPIC}")
    while True:
        for v in vehicles:
            msg = generate_ping(v[0], v[1], v[2])
            producer.send(TOPIC, msg)
        producer.flush()
        time.sleep(1)  # 1 second per batch

if __name__ == "__main__":
    main()
