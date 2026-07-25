import requests
import streamlit as st

try:
    from config import WAQI_TOKEN
except ImportError:
    WAQI_TOKEN = st.secrets["WAQI_TOKEN"]
import requests
from config import WAQI_TOKEN

def get_live_aqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "ok":
        return None

    return {
        "city": data["data"]["city"]["name"],
        "aqi": data["data"]["aqi"],
        "dominant_pollutant": data["data"].get("dominentpol", "N/A"),
        "pollutants": data["data"].get("iaqi", {}),
        "time": data["data"]["time"]["s"]
    }
if __name__ == "__main__":
    result = get_live_aqi("delhi")
    print(result)