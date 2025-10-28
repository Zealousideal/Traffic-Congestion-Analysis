"""
Simple GPS simulator that produces JSON pings to Kafka topic 'gps.pings'. This is the Kafka producer 
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
    api_version=(0, 10)  # Important fix
)

# Generate fake GPS pings
def generate_ping(vehicle_id, lat, lon):
    lat_jitter = random.uniform(-0.01, 0.01)
    lon_jitter = random.uniform(-0.01, 0.01)

    return {
        "vehicle_id": vehicle_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lat": lat + lat_jitter,
        "lon": lon + lon_jitter,
        "speed_kmph": round(max(0.0, random.gauss(30, 12)), 2),
        "source": "sim"
    }

def main():
    vehicles = []

    # Multi-city centers added + named for debugging
    centers = [
        ("Bengaluru", 12.9716, 77.5946),
        ("Delhi", 28.6139, 77.2090),
        ("Mumbai", 19.0760, 72.8777),
        ("Kolkata", 22.5726, 88.3639),
    ]

    num_vehicles_per_city = 10000  
    spread = 0.02  #  control spread around city center

    total = num_vehicles_per_city * len(centers)

    # Proper distribution among multiple cities
    for city_name, lat, lon in centers:
        for i in range(num_vehicles_per_city):
            vehicles.append((
                f"{city_name}_veh_{i}",
                lat + random.uniform(-spread, spread),  # use spread correctly
                lon + random.uniform(-spread, spread)
            ))

    print(f"🚗 Total Vehicles Streaming: {total}")
    print(f"Producing live traffic to Kafka → {TOPIC}")

    # Stream forever
    while True:
        for v in vehicles:
            msg = generate_ping(v[0], v[1], v[2])
            producer.send(TOPIC, msg)
        producer.flush()
        time.sleep(1)  #  ~4000 messages per second (scalable)

if __name__ == "__main__":
    main()
