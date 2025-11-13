import streamlit as st
import pandas as pd
import geocoder
import plotly.express as px

# ==============================
# Load Dataset
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed/normalized_weather_data.csv")   # your dataset
    return df

df = load_data()

# ==============================
# Get User Location
# ==============================
g = geocoder.ip('me')
user_country = g.country
user_continent = g.continent

# Fallback if geocoder fails
if user_country is None:
    user_country = "India"
if user_continent is None:
    user_continent = "Asia"

# ==============================
# Sidebar — Continent and Country Filters
# ==============================
st.title("🌍 Global Weather Map")

# Continent selection
continents = sorted(df['continent'].dropna().unique())
selected_continents = st.multiselect(
    "Select Continent",
    continents,
    default=[user_continent] if user_continent in continents else []
)

# Country selection grouped by continent
filtered_countries = df[df['continent'].isin(selected_continents)]
country_options = sorted(filtered_countries['country'].dropna().unique())

selected_countries = st.multiselect(
    "Select Country",
    options=country_options,
    default=[user_country] if user_country in country_options else []
)

# Count of continents and countries
st.subheader(f"🌐 {len(selected_continents)} Continent(s) | 🏳️ {len(selected_countries)} Country(ies) selected")

# ==============================
# Weather Overview Metrics
# ==============================
if selected_countries:
    country_data = df[df['country'].isin(selected_countries)]

    # Take latest values (or mean) for metrics
    humidity = round(country_data['humidity'].mean(), 1)
    wind_speed = round(country_data['wind_speed'].mean(), 1)
    visibility = round(country_data['visibility'].mean(), 1)
    pressure = round(country_data['pressure'].mean(), 1)
    uv_index = round(country_data['uv_index'].mean(), 1)
    precipitation = round(country_data['precipitation'].mean(), 2)
    temp = round(country_data['temperature_celsius'].mean(), 1)

    col_sun1, col_sun2 = st.columns(2)
    col_sun1.metric("🌅 Sunrise", country_data['sunrise'].iloc[0] if 'sunrise' in country_data.columns else "N/A")
    col_sun2.metric("🌇 Sunset", country_data['sunset'].iloc[0] if 'sunset' in country_data.columns else "N/A")

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("🌡️ Temp", f"{temp} °C")
    c2.metric("💧 Humidity", f"{humidity} %")
    c3.metric("🌬️ Wind Speed", f"{wind_speed} Kph")
    c4.metric("👁️ Visibility", f"{visibility} km")
    c5.metric("📊 Pressure", f"{pressure} mm")
    c6.metric("☀️ UV Index", f"{uv_index}")
    c7.metric("🌧️ Precipitation", f"{precipitation} mm")

# ==============================
# Visualization Options
# ==============================
st.subheader("📊 Visualization Options")

graph_type = st.selectbox(
    "Select Graph Type",
    ["Bar Chart", "Line Chart", "Choropleth Map", "Scatter Plot", "Box Plot", "Heatmap"]
)

if selected_countries:
    plot_data = df[df['country'].isin(selected_countries)]

    if graph_type == "Bar Chart":
        fig = px.bar(plot_data, x='country', y='temperature_celsius', color='continent', title='Average Temperature')

    elif graph_type == "Line Chart":
        fig = px.line(plot_data, x='date', y='temperature_celsius', color='country', title='Temperature Trend')

    elif graph_type == "Choropleth Map":
        fig = px.choropleth(plot_data,
                            locations="country",
                            locationmode="country names",
                            color="temperature_celsius",
                            title="Global Temperature Distribution")

    elif graph_type == "Scatter Plot":
        fig = px.scatter(plot_data,
                         x='temperature_celsius', y='humidity',
                         color='country', size='uv_index',
                         title="Temperature vs Humidity")

    elif graph_type == "Box Plot":
        fig = px.box(plot_data, x='country', y='temperature_celsius', color='continent', title='Temperature Spread')

    elif graph_type == "Heatmap":
        pivot = plot_data.pivot_table(index='country', columns='date', values='temperature_celsius')
        fig = px.imshow(pivot, aspect='auto', title="Temperature Heatmap")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please select at least one country to visualize data.")
