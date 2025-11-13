# climatescope/dashboard/app.py
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from datetime import datetime
from io import StringIO

st.set_page_config(
    page_title="Global Weather Repository — Climatescope",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_data(path=".. /data/processed/normalized_weather_data.csv"):
    # default path - adjust if you place app at repo root
    df = pd.read_csv(path)
    # Ensure datetime
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    # Lat/Lon
    for col in ["latitude", "longitude"]:
        if col not in df.columns:
            df[col] = np.nan
    # Basic numeric cast for common columns if present
    numeric_cols = [
        "temperature_celsius", "wind_mph", "wind_degree", "humidity",
        "air_quality_us-epa-index", "air_quality_gb-defra-index"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# ---- LOAD DATA ----
DATA_PATH = "../data/processed/normalized_weather_data.csv"  # adjust as needed
df = load_data(DATA_PATH)

# ---- SIDEBAR CONTROLS ----
st.sidebar.header("Filters & Controls")

# Country filter
countries = sorted(df["country"].dropna().unique())
selected_countries = st.sidebar.multiselect("Select countries (top 20 shown)", countries[:200], default=countries[:6])

# Location filter (dependent)
if selected_countries:
    locs = df[df["country"].isin(selected_countries)]["location_name"].dropna().unique()
else:
    locs = df["location_name"].dropna().unique()
selected_locations = st.sidebar.multiselect("Locations", list(locs), max_selections=20)

# Date range
if "last_updated" in df.columns and df["last_updated"].notna().any():
    min_date = df["last_updated"].min().date()
    max_date = df["last_updated"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
else:
    date_range = None

# Feature selection for clustering
feature_options = [c for c in ["temperature_celsius", "humidity", "wind_mph", "air_quality_us-epa-index"] if c in df.columns]
cluster_features = st.sidebar.multiselect("Features for clustering", feature_options, default=feature_options[:2])

# Clustering controls
use_clustering = st.sidebar.checkbox("Enable clustering (KMeans)", value=False)
n_clusters = st.sidebar.slider("Number of clusters", 2, 8, 4) if use_clustering else 2

st.sidebar.markdown("---")
st.sidebar.write("Export filtered data:")
st.sidebar.write("· Use the button below to download the currently filtered dataset as CSV.")

# ---- FILTER DF ----
filtered = df.copy()
if selected_countries:
    filtered = filtered[filtered["country"].isin(selected_countries)]
if selected_locations:
    filtered = filtered[filtered["location_name"].isin(selected_locations)]
if date_range and "last_updated" in filtered.columns:
    start, end = date_range
    filtered = filtered[(filtered["last_updated"].dt.date >= start) & (filtered["last_updated"].dt.date <= end)]

# ---- TOP ROW METRICS ----
st.title("Climatescope — Global Weather Repository 🌍")
st.markdown("Interactive dashboard for global station/weather snapshots. Use the sidebar to filter and explore.")

col1, col2, col3, col4 = st.columns(4)
def safe_mean(df, col):
    return df[col].mean() if col in df.columns and df[col].notna().any() else np.nan

col1.metric("Avg Temperature (°C)", f"{safe_mean(filtered, 'temperature_celsius'):.2f}")
col2.metric("Avg Humidity (%)", f"{safe_mean(filtered, 'humidity'):.2f}")
col3.metric("Avg Wind (mph)", f"{safe_mean(filtered, 'wind_mph'):.2f}")
col4.metric("Avg AQI (US-EPA)", f"{safe_mean(filtered, 'air_quality_us-epa-index'):.2f}")

st.markdown("---")

# ---- FIXED MAP SECTION ----
st.subheader("Global map — stations")
map_df = filtered.dropna(subset=["latitude", "longitude"]).copy()

if map_df.empty:
    st.info("No geolocated stations found for the selected filters.")
else:
    # Precompute color scale in Python
    if "temperature_celsius" in map_df.columns:
        t_min = map_df["temperature_celsius"].min()
        t_max = map_df["temperature_celsius"].max()
        # Avoid division by zero
        if t_min == t_max:
            map_df["color_r"] = 200
        else:
            map_df["color_r"] = ((map_df["temperature_celsius"] - t_min) / (t_max - t_min) * 255).astype(int)
        map_df["color_g"] = 120
        map_df["color_b"] = 200
    else:
        map_df["color_r"] = 100
        map_df["color_g"] = 180
        map_df["color_b"] = 120

    map_df["color"] = map_df[["color_r", "color_g", "color_b"]].values.tolist()

    midpoint = (map_df["latitude"].mean(), map_df["longitude"].mean())
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_fill_color="color",
        get_radius=20000,
        pickable=True,
        auto_highlight=True,
    )
    view_state = pdk.ViewState(
        longitude=midpoint[1], latitude=midpoint[0], zoom=1.5, pitch=30
    )
    tooltip = {
        "html": "<b>{location_name}</b><br/>Country: {country}<br/>Temp: {temperature_celsius} °C<br/>Humidity: {humidity}<br/>Last updated: {last_updated}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
    st.pydeck_chart(deck)

# ---- STATION LIST WITH INLINE FILTERS ----
st.subheader("Station list (filtered)")

if not map_df.empty:
    # Inline filters (dropdown)
    unique_countries = sorted(map_df["country"].dropna().unique())
    selected_country_table = st.selectbox(
        "Filter by Country (Table only)", 
        options=["All"] + unique_countries, 
        index=0
    )

    if selected_country_table != "All":
        df_table = map_df[map_df["country"] == selected_country_table].copy()
    else:
        df_table = map_df.copy()

    unique_locations = sorted(df_table["location_name"].dropna().unique())
    selected_location_table = st.selectbox(
        "Filter by Location (Table only)",
        options=["All"] + unique_locations,
        index=0
    )

    if selected_location_table != "All":
        df_table = df_table[df_table["location_name"] == selected_location_table]

    # Columns to display in the table
    table_columns = [
        "country", 
        "location_name", 
        "latitude", 
        "longitude", 
        "last_updated", 
        "temperature_celsius"
    ]
    if "humidity" in df_table.columns:
        table_columns.append("humidity")
    if "wind_mph" in df_table.columns:
        table_columns.append("wind_mph")

    st.dataframe(
        df_table[table_columns]
        .sort_values("country")
        .reset_index(drop=True),
        use_container_width=True
    )
else:
    st.info("No data available for table display.")



# ---- Weather Condition Breakdown + Moon Phase / Sunrise-Sunset ----
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.subheader("Weather condition breakdown")
    if "condition_text" in filtered.columns:
        cond = filtered["condition_text"].value_counts().reset_index()
        cond.columns = ["condition", "count"]
        fig2 = px.bar(cond.head(20), x="count", y="condition", orientation="h", title="Top weather conditions")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No 'condition_text' column in dataset.")

with c2:
    st.subheader("Moon phase & Sunrise / Sunset Overview")
    cols = []
    if "moon_phase" in filtered.columns: cols.append("moon_phase")
    if "sunrise" in filtered.columns: cols.append("sunrise")
    if "sunset" in filtered.columns: cols.append("sunset")
    if cols:
        sample = filtered[cols].dropna().head(200)
        st.dataframe(sample)
    else:
        st.write("No moon/sun columns available in the data slice.")

# ---- CLUSTERING + PCA ----
st.markdown("---")
st.header("Station similarity: Clustering & PCA")
cluster_ready = filtered.dropna(subset=cluster_features + ["latitude", "longitude"]) if cluster_features else pd.DataFrame()

if use_clustering and cluster_ready.shape[0] >= n_clusters:
    X = cluster_ready[cluster_features].copy()
    # normalize
    X_scaled = (X - X.mean()) / X.std(ddof=0)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    cluster_ready = cluster_ready.assign(cluster=labels)
    st.write(f"Clustering performed on {len(cluster_ready)} stations using features: {', '.join(cluster_features)}")

    # PCA 2D
    pca = PCA(n_components=2, random_state=42)
    comps = pca.fit_transform(X_scaled.fillna(0))
    cluster_ready["pc1"], cluster_ready["pc2"] = comps[:, 0], comps[:, 1]

    fig_pca = px.scatter(
        cluster_ready,
        x="pc1",
        y="pc2",
        color=cluster_ready["cluster"].astype(str),
        hover_data=["location_name", "country", *cluster_features],
        title="PCA projection of clusters"
    )
    st.plotly_chart(fig_pca, use_container_width=True)

    # Cluster map
    fig_map = px.scatter_mapbox(
        cluster_ready,
        lat="latitude",
        lon="longitude",
        color=cluster_ready["cluster"].astype(str),
        size=cluster_ready[cluster_features[0]] if cluster_features else None,
        hover_name="location_name",
        hover_data=["country"] + cluster_features,
        zoom=1,
        height=500,
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

else:
    st.info("Clustering disabled or not enough stations for clustering. Select features and enable clustering.")

# ---- DOWNLOAD FILTERED DATA ----
st.markdown("---")
st.subheader("Export / Save")

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

if not filtered.empty:
    csv_bytes = convert_df_to_csv(filtered)
    st.download_button("Download filtered data (CSV)", csv_bytes, file_name="filtered_weather.csv", mime="text/csv")

# Quick inline preview and small data table export
st.write(f"Filtered stations: {len(filtered)} rows")
st.dataframe(filtered.head(200))

# ---- FOOTER / HELP ----
st.markdown("---")
st.markdown(
    """
    **Tips**
    - Use the sidebar to combine filters (country, location, date range) — dashboards update instantly.
    - Enable clustering to find groups of stations with similar readings.
    - Adjust the `DATA_PATH` at the top of this file if your CSV path differs.
    """
)
st.caption("Built for the GlobalWeatherRepository — Climatescope. (Streamlit app)")
