# dashboard/components/metrics.py
import streamlit as st

def create_metric_cards(df):
    """Create beautiful metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("🌡️ Temperature", "temperature_celsius", "°C"),
        ("💨 Wind Speed", "wind_mph", " mph"),
        ("💧 Humidity", "humidity", "%"),
        ("🌤️ Cloud Cover", "cloud", "%")
    ]
    
    for col, (label, column, unit) in zip([col1, col2, col3, col4], metrics):
        with col:
            if column in df.columns:
                value = df[column].mean()
                std = df[column].std()
                st.metric(label=label, value=f"{value:.2f}{unit}", delta=f"{std:.2f}{unit} std")