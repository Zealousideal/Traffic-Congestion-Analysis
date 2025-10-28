<p align="center">
  <img src="https://img.shields.io/badge/Smart%20City%20Traffic-Real--Time%20Analytics-FF4B4B?style=for-the-badge&logo=google-maps&logoColor=white"/>
</p>

<h1 align="center">🚦 Real-Time Traffic Congestion Prediction</h1>
<h3 align="center">AI • Big Data • Streaming • Smart Cities</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Kafka-Streaming-black?style=flat-square&logo=apache-kafka"/>
  <img src="https://img.shields.io/badge/Redis-In--Memory-red?style=flat-square&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi"/>
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit"/>
  <img src="https://img.shields.io/badge/Docker-Orchestration-2496ED?style=flat-square&logo=docker"/>
</p>

## System Architecture

<p align="center">
  <img src="https://img.shields.io/badge/Data%20Flow-Kafka%20→%20ML%20→%20Redis%20→%20Dashboard-blue?style=for-the-badge"/>
</p>
The solution consists of distributed components connected through a streaming data pipeline:

* **Kafka Producer** — Simulates live GPS pings from vehicles
* **Kafka Broker + Zookeeper** — Message streaming backbone
* **Stream Processor** — Aggregates data per road segment and performs ML predictions
* **Redis** — In-memory storage for latest segment states
* **FastAPI Model Server** — Provides REST endpoints for predictions and live segment data
* **Streamlit Dashboard** — Interactive traffic map and latest congestion insights

## Data Flow

1. Simulated vehicles generate geospatial data in Bangalore
2. Kafka streams the data to the processing layer
3. The processor extracts speed features, calculates vehicle density, and predicts congestion probability using a trained model
4. Latest segment predictions are cached in Redis
5. Dashboard pulls live congestion data from Redis to visualize city traffic

## Machine Learning Model

A `RandomForestClassifier` is trained on synthetic traffic patterns.
Key features include:

* Average speed on segment
* Vehicle count per segment window
* Time of day (hour feature)

The trained model (`model.pkl`) is loaded during inference inside the stream processor.

## 🛠️ Technology Stack

<table align="center">
<tr>
<td align="center"><img src="https://www.vectorlogo.zone/logos/apache_kafka/apache_kafka-icon.svg" width="40"/><br><b>Kafka</b></td>
<td align="center"><img src="https://www.vectorlogo.zone/logos/redis/redis-icon.svg" width="40"/><br><b>Redis</b></td>
<td align="center"><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" width="40"/><br><b>FastAPI</b></td>
<td align="center"><img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width="40"/><br><b>Streamlit</b></td>
<td align="center"><img src="https://www.vectorlogo.zone/logos/docker/docker-icon.svg" width="40"/><br><b>Docker</b></td>
</tr>
</table>

| Layer             | Technology                                |
| ----------------- | ----------------------------------------- |
| Data Ingestion    | Kafka, Zookeeper                          |
| Stream Processing | Python Kafka Consumer                     |
| Machine Learning  | Scikit-learn                              |
| Serving Layer     | FastAPI, Uvicorn                          |
| Cache Store       | Redis                                     |
| Visualization     | Streamlit, Mapbox                         |
| Deployment        | Docker, Docker Compose, GitHub Codespaces |

## How to Run

### 1️⃣ Launch the entire platform

```bash
docker compose up --build
```

### 2️⃣ Access interfaces

| Component           | URL                          | Notes                        |
| ------------------- | ---------------------------- | ---------------------------- |
| Streamlit Dashboard | `http://localhost:8501`      | Live traffic visualization   |
| FastAPI Docs        | `http://localhost:8000/docs` | REST test UI for predictions |

*(Codespaces users must set ports 8501 & 8000 visibility to Public.)*

---

## Project Structure

```
Traffic-Congestion-Analysis/
├── docker-compose.yml
├── producer/
│   ├── producer.py
│   ├── Dockerfile
│   └── requirements.txt
├── stream_processor/
│   ├── processor.py
│   ├── Dockerfile
│   └── requirements.txt
├── trainer/
│   ├── train.py
│   ├── Dockerfile
│   └── requirements.txt
├── model_server/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── dashboard/
    ├── app.py
    ├── Dockerfile
    └── .streamlit/config.toml
```

---

## Features

* Real-time ingestion of live GPS data
* Continuous model-based congestion prediction
* Geospatial clustering into road segments
* Live monitoring and auto-refresh dashboard
* Fully containerized multi-service architecture

## Use Cases

* Smart traffic control centers
* Congestion alert systems
* Infrastructure planning analytics
* Urban mobility research and simulation

<hr>

<p align="center">
  <img src="https://img.shields.io/badge/Smart%20City%20AI-Innovation%20Made%20Simple-20232A?style=for-the-badge"/>
</p>
