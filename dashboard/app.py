import streamlit as st
import requests
import pandas as pd
import time

API = "http://model_server:8000"

st.set_page_config(layout="wide", page_title="Traffic Congestion PoC")
st.title("Traffic Congestion — Live PoC (Docker)")

def fetch_segments():
    try:
        r = requests.get(f"{API}/segments/latest")
        j = r.json()
        segs = j.get("segments", [])
        if not segs:
            return pd.DataFrame()
        # convert to DataFrame and try to extract lat/lon from segment id S_lat_lon
        rows = []
        for s in segs:
            segid = s.get("road_segment_id")
            ts = s.get("ts")
            avg_speed = float(s.get("avg_speed", 0))
            vehicle_count = int(s.get("vehicle_count", 0))
            prob = float(s.get("congestion_prob", 0))
            lat = None; lon = None
            if segid and segid.startswith("S_"):
                parts = segid.split("_")
                try:
                    lat = float(parts[1]); lon = float(parts[2])
                except:
                    lat = None; lon = None
            rows.append({"road_segment_id": segid, "ts": ts, "avg_speed": avg_speed, "vehicle_count": vehicle_count, "congestion_prob": prob, "lat": lat, "lon": lon})
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error fetching segments: {e}")
        return pd.DataFrame()

st.sidebar.markdown("## Controls")
refresh = st.sidebar.checkbox("Auto-refresh", value=True)
interval = st.sidebar.slider("Refresh interval (sec)", min_value=1, max_value=10, value=2)

placeholder = st.empty()

while True:
    df = fetch_segments()
    with placeholder.container():
        st.subheader("Latest segment predictions")
        if df.empty:
            st.info("No data yet. Start the producer and give it a few seconds.")
        else:
            df_sorted = df.sort_values("congestion_prob", ascending=False).head(200)
            st.dataframe(df_sorted[["road_segment_id","ts","avg_speed","vehicle_count","congestion_prob"]])
            # Map display requires lat & lon
            df_map = df_sorted.dropna(subset=["lat","lon"])
            if not df_map.empty:
                st.map(df_map.rename(columns={"lat":"latitude","lon":"longitude"})[["latitude","longitude"]].drop_duplicates())
    if not refresh:
        break
    time.sleep(interval)
