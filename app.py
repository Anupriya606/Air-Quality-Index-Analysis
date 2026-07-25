import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

from utils.data_loader import load_aqi_data, preprocess_aqi_data, get_country_rankings
from utils.live_api import get_live_aqi
from utils.forecasting import load_or_train_model, predict_category

st.set_page_config(page_title="Global AQI Analysis", page_icon="🌍", layout="wide")

# Load custom CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<style>[data-testid="stAppViewContainer"] { background: transparent; }</style>', unsafe_allow_html=True)

# Load & cache data so it doesn't reload on every interaction
@st.cache_data
def get_data():
    df = load_aqi_data("data/global_aqi.csv")
    df = preprocess_aqi_data(df)
    return df

df = get_data()
model, encoder, accuracy = load_or_train_model(df)

st.sidebar.title("🌍 Global AQI Dashboard")
page = st.sidebar.radio("Navigate", ["Live AQI", "World Map", "Country Rankings", "Pollutant Analysis", "Predict AQI Category"])

if page == "Live AQI":
    st.title("🔴 Live Air Quality Lookup")
    city = st.text_input("Enter a city name", "Delhi")

    if st.button("Get Live AQI"):
        result = get_live_aqi(city)
        if result is None:
            st.error("City not found or API issue. Try another city name.")
        else:
            aqi = result["aqi"]
            color = "green" if aqi <= 50 else "orange" if aqi <= 100 else "red" if aqi <= 200 else "darkred"

            col1, col2 = st.columns([1, 2])
            with col1:
                fig = px.pie(values=[aqi, max(0, 300-aqi)], hole=0.7,
                             color_discrete_sequence=[color, "#222"])
                fig.update_traces(textinfo='none')
                fig.update_layout(showlegend=False, annotations=[dict(text=str(aqi), font_size=40, showarrow=False)])
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.metric("City", result["city"])
                st.caption("📍 Reading from the nearest available monitoring station for this location.")
                st.metric("Dominant Pollutant", result["dominant_pollutant"].upper())
                st.metric("Last Updated", result["time"])

                if aqi <= 50:
                    st.success("✅ Good — air quality is safe.")
                elif aqi <= 100:
                    st.warning("⚠️ Moderate — sensitive groups should be cautious.")
                elif aqi <= 200:
                    st.error("🚫 Unhealthy — limit outdoor activity.")
                else:
                    st.error("☠️ Hazardous — avoid outdoor exposure.")

elif page == "World Map":
    st.title("🗺️ Global AQI Map")

    def get_color(aqi):
        if aqi <= 50: return [0, 200, 0]
        elif aqi <= 100: return [255, 165, 0]
        elif aqi <= 200: return [255, 0, 0]
        else: return [139, 0, 0]

    map_df = df.copy()
    map_df["color"] = map_df["AQI Value"].apply(get_color)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["lng", "lat"],
        get_fill_color="color",
        get_radius=15000,
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state,
                              tooltip={"text": "{City}, {Country}\nAQI: {AQI Value}"}))

elif page == "Country Rankings":
    st.title("📊 Country AQI Rankings")
    rankings = get_country_rankings(df)

    top_n = st.slider("Show top N most polluted countries", 5, 30, 15)
    fig = px.bar(rankings.head(top_n), x="AQI Value", y="Country", orientation="h",
                 color="AQI Value", color_continuous_scale="Reds")
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

elif page == "Pollutant Analysis":
    st.title("🧪 Pollutant Correlation Analysis")
    pollutant_cols = ['AQI Value', 'CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']
    corr = df[pollutant_cols].corr()

    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", aspect="auto")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Values close to 1 mean pollutants rise together; close to 0 means little relationship.")

elif page == "Predict AQI Category":
    st.title("🤖 AQI Category Predictor")
    if accuracy:
        st.caption(f"Model trained — test accuracy: {accuracy:.2%}")

    col1, col2 = st.columns(2)
    with col1:
        co = st.number_input("CO AQI Value", 0, 500, 5)
        ozone = st.number_input("Ozone AQI Value", 0, 500, 30)
    with col2:
        no2 = st.number_input("NO2 AQI Value", 0, 500, 10)
        pm25 = st.number_input("PM2.5 AQI Value", 0, 500, 50)

    if st.button("Predict"):
        category = predict_category(model, encoder, co, ozone, no2, pm25)
        st.success(f"Predicted AQI Category: **{category}**")