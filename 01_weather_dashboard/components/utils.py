import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data():
    # Get path relative to this file (components/utils.py)
    base_dir = os.path.dirname(os.path.dirname(__file__))  # components -> weather_dashboard root
    file_path = os.path.join(base_dir, "..", "data", "processed", "processed_weather_data.csv")
    
    df = pd.read_csv(file_path)
    
    # Ensure required columns exist
    required_cols = ["country", "location_name", "latitude", "longitude",
                     "temperature_celsius", "humidity", "wind_mph"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
    
    return df
