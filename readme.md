# 🚦 Predict Traffic Congestion Using Big Data Analytics

An end-to-end, **dockerized streaming analytics system** that predicts real-time traffic congestion using simulated GPS and sensor data.

## 📊 Architecture Overview
- **Data Ingestion** → Kafka (from simulated GPS)
- **Stream Processing** → Python/Kafka Consumer (windowed aggregation + ML inference)
- **Model Training** → RandomForest on synthetic traffic data
- **Storage** → Redis (hotstore for latest segment states)
- **Visualization** → Streamlit Dashboard
- **Serving** → FastAPI model API

<p align="center">
  <img src="docs/architecture.png" width="600">
</p>

## 🧠 Tech Stack
- Docker & Docker Compose
- Apache Kafka, Redis
- Python (FastAPI, Streamlit, scikit-learn)
- Joblib, Pandas, Requests

## 🚀 Quickstart
```bash
git clone https://github.com/<your-username>/traffic-poc.git
cd traffic-poc
docker-compose up --build
