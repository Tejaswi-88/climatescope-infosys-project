# ===============================
# 🌦️ Global Weather Condition Analysis Dashboard (Enhanced)
# ===============================
import streamlit as st
import pandas as pd
import pycountry_convert as pc
import plotly.express as px
import requests

# ✅ Access global dataset and filters
from components.data_loader import get_global_data
from components.sidebar_filters import sidebar_location_filters, get_user_country_and_continent

# -----------------------------
# 📦 Load global dataset once
# -----------------------------
df = get_global_data()

# -----------------------------
# 🌍 Sidebar Filters (shared)
# -----------------------------
df_filtered = sidebar_location_filters(df)

selected_continents = st.session_state.get("continent", [])
selected_countries = st.session_state.get("country", [])
selected_locations = st.session_state.get("location", [])


# Ensure datetime columns exist
if "last_updated" in df.columns:
    df["date"] = pd.to_datetime(df["last_updated"])
elif "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
else:
    # If no date column exists, you must create Year, Month, Day another way
    st.error("No datetime column found in dataset. Please include 'date' or 'last_updated'.")
    st.stop()

# Extract Year, Month, Day
df["Year"] = df["date"].dt.year
df["Month"] = df["date"].dt.month
df["Day"] = df["date"].dt.day


# ===============================
# 🎨 Sidebar Styling
# ===============================
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000, #1A1A1A);
        color: #F2F2F2;
        box-shadow: 0 0 15px rgba(255,0,0,0.2);
    }
    [data-testid="stSidebarNav"]::before {
        content: "🧭 NAVIGATION";
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #FF3B3B !important;
        margin: 6px 8px 4px 8px !important;
        display: block;
    }
    [data-testid="stSidebarNav"] ul li div[data-selected="true"] {
        background: rgba(255,59,59,0.2) !important;
        border-left: 3px solid #FF3B3B !important;
        color: #FF3B3B !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================
# Page Config
# ============================
st.set_page_config(page_title="Weather Condition Analysis", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; width:100%; font-size: 48px; font-family: "Segoe UI", sans-serif;margin-top: -50px;'>
        🌤️ Global Weather Condition Analysis Dashboard
    </h1>
""", unsafe_allow_html=True)

def styled_header(text, level=2, color="rgb(255, 140, 66)", size=30):
    html = f"""
        <h{level} style='
            color: {color};
            font-size: {size}px;
            font-weight: 600;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
            font-family: "Segoe UI", sans-serif;
            margin-top: 10px;
            margin-bottom: 0px;
        '>
            {text}
        </h{level}>
    """
    st.markdown(html, unsafe_allow_html=True)


st.markdown("""<h6 style=
            'font-size: 16px;
            font-weight: 200;
            color: #A0A0A0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-family: "Segoe UI", sans-serif;
            text-align:center;
            margin-bottom: 20px;
        '>
Explore weather patterns and trends by continent, country, or location.
</h6>""", unsafe_allow_html=True)

# ============================
# 🔧 Helper: Continent Lookup
# ============================
def country_to_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe',
            'NA': 'North America', 'OC': 'Oceania',
            'SA': 'South America', 'AN': 'Antarctica'
        }[continent_code]
    except:
        return "Unknown"

# ============================
# 🧭 Temporal Filters
# ============================
st.sidebar.header("📆 Temporal Filters")

years = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect(
    "📆 Select Year(s)",
    options=years,
    default=[max(years)] if years else None,
)

months = sorted(df[df["Year"].isin(selected_years)]["Month"].unique()) if selected_years else sorted(df["Month"].unique())
selected_months = st.sidebar.multiselect("🗓️ Select Month(s)", options=months, default=None)

days = sorted(df[df["Month"].isin(selected_months)]["Day"].unique()) if selected_months else sorted(df["Day"].unique())
selected_days = st.sidebar.multiselect("📅 Select Day(s)", options=days, default=None)

# Filter by time
df_filtered = df_filtered[
    (df_filtered["Year"].isin(selected_years))
    & (df_filtered["Month"].isin(selected_months) if selected_months else True)
    & (df_filtered["Day"].isin(selected_days) if selected_days else True)
]

# ============================
# 📊 Grouping Level Selector
# ============================
st.markdown("#### 🧭 Choose Analysis Level")
group_level = st.radio(
    "View analysis by:",
    ["Continent", "Country", "Location"],
    index=1,
    horizontal=True,
)

group_col = (
    "continent" if group_level == "Continent"
    else "country" if group_level == "Country"
    else "location_name"
)

# ============================
# 🌦️ Weather Condition Overview
# ============================
styled_header(f"🌦️ Weather Condition Overview by {group_level}")

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
else:
    # Frequency table
    condition_group = df_filtered.groupby(["condition_text", group_col]).size().reset_index(name="Count")

    # Build hover text with per-location counts
    hover_df = (
        condition_group.groupby("condition_text")[["Count", group_col]]
        .apply(lambda x: "<br>".join([f"{lvl} ({cnt})" for lvl, cnt in zip(x[group_col], x["Count"])]))
        .reset_index(name="hover_text")
    )
    merged_df = pd.merge(condition_group, hover_df, on="condition_text", how="left")

    # Plot
    fig_count = px.bar(
        merged_df,
        x="condition_text",
        y="Count",
        color=group_col,
        title=f"🌦️ Frequency of Weather Conditions by {group_level}",
        text_auto=True,
        hover_name="condition_text",
        hover_data={"hover_text": False, group_col: True, "Count": True},
    )

    fig_count.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        customdata=merged_df[["hover_text"]],
    )

    fig_count.update_layout(
        xaxis_title="Weather Condition",
        yaxis_title="Frequency",
        legend_title=group_level,
        xaxis_tickangle=45,
        bargap=0.25,
        height=600,
    )

    st.plotly_chart(fig_count, use_container_width=True)

    # --------------------
    # Most / Least Observed
    # --------------------
    total_counts = df_filtered["condition_text"].value_counts().reset_index()
    total_counts.columns = ["Condition", "Count"]
    most_common = total_counts.iloc[0]
    least_common = total_counts.iloc[-1]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🌞 Most Observed", value=most_common["Condition"], delta=most_common["Count"])
    with col2:
        st.metric(label="🌧️ Least Observed", value=least_common["Condition"], delta=-least_common["Count"])

    # ============================
    # ⏳ Weather Condition Trends Over Time
    # ============================
    styled_header("⏳ Weather Condition Trends Over Time")

    # --- Trend Level Selection ---
    trend_level = st.radio(
        "📈 Select Trend Granularity:",
        options=["Yearly", "Monthly", "Daily"],
        index=1,
        horizontal=True,
    )

    # --- Weather Condition Filter ---
    all_conditions = sorted(df_filtered["condition_text"].dropna().unique().tolist())

    # Add an "All" option to the top
    condition_selection = st.multiselect(
        "🌦️ Select Weather Condition(s) to Display:",
        options=["All"] + all_conditions,
        default=["All"],
        help="Choose one or more specific weather conditions, or select 'All' to show all conditions."
    )

    # --- Handle All Option Behavior ---
    if "All" in condition_selection:
        # If 'All' is selected, ignore other selections
        selected_conditions = all_conditions
        disable_other_options = True
    else:
        selected_conditions = condition_selection
        disable_other_options = False

    # Filter data based on selected conditions
    df_trend_filtered = df_filtered[df_filtered["condition_text"].isin(selected_conditions)]

    # --- Prepare Trend Data ---
    if trend_level == "Yearly":
        time_trend = (
            df_trend_filtered.groupby(["Year", "condition_text"])
            .size()
            .reset_index(name="Count")
        )
        fig_trend = px.line(
            time_trend,
            x="Year",
            y="Count",
            color="condition_text",
            markers=True,
            title="🌍 Yearly Weather Trends by Condition",
            hover_data=["condition_text", "Year", "Count"],
        )

    elif trend_level == "Monthly":
        time_trend = (
            df_trend_filtered.groupby(["Year", "Month", "condition_text"])
            .size()
            .reset_index(name="Count")
        )
        time_trend["Period"] = (
            time_trend["Year"].astype(str) + "-" + time_trend["Month"].astype(str).str.zfill(2)
        )
        fig_trend = px.line(
            time_trend,
            x="Period",
            y="Count",
            color="condition_text",
            markers=True,
            title="📅 Monthly Weather Trends by Condition",
            hover_data=["condition_text", "Year", "Month", "Count"],
        )

    else:  # Daily
        if "last_updated" in df_trend_filtered.columns:
            df_trend_filtered["Date"] = df_trend_filtered["last_updated"].dt.date
        elif "date" in df_trend_filtered.columns:
            df_trend_filtered["Date"] = pd.to_datetime(df_trend_filtered["date"]).dt.date
        else:
            df_trend_filtered["Date"] = pd.to_datetime(
                df_trend_filtered[["Year", "Month", "Day"]]
                .astype(str)
                .agg("-".join, axis=1)
            ).dt.date

        time_trend = (
            df_trend_filtered.groupby(["Date", "condition_text"])
            .size()
            .reset_index(name="Count")
        )
        fig_trend = px.line(
            time_trend,
            x="Date",
            y="Count",
            color="condition_text",
            markers=True,
            title="📆 Daily Weather Trends by Condition",
            hover_data=["condition_text", "Date", "Count"],
        )

    # --- Chart Layout ---
    fig_trend.update_layout(
        xaxis_title="Time Period",
        yaxis_title="Observation Count",
        template="plotly_dark",
        hovermode="x unified",
        legend_title_text="Weather Condition",
    )

    st.plotly_chart(fig_trend, use_container_width=True)


    # ============================
    # 🌡️ Weather Conditions vs Meteorological Factors
    # ============================
    styled_header("🌡️ Weather Conditions vs Meteorological Factors")
    with st.expander("📘 What This Graph Shows", expanded=False):

        st.markdown("""
            <div style='background-color:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #4CAF50;'>
            <p style='color:#ddd;'>
            This visualization explores how different <b>meteorological factors</b> — such as <b>temperature</b>,
            <b>humidity</b>, <b>wind speed</b>, <b>UV index</b>, <b>precipitation</b>, and <b>pressure</b> — influence
            various <b>weather conditions</b> across locations.
            </p>

            <ul style='color:#ccc;'>
            <li>Each point represents a single weather observation.</li>
            <li>Colors indicate different <b>weather conditions</b> (e.g., Sunny, Rainy, Cloudy).</li>
            <li>Hover over points to view details like <b>temperature, humidity, and location</b>.</li>
            <li>Enable <b>Advanced Comparison</b> to choose your own X and Y factors for deeper insights.</li>
            </ul>

            <p style='color:#ccc;'>
            This helps identify patterns — for example, <b>higher humidity often aligns with cloudy conditions</b>,
            while <b>strong UV levels are linked with clearer skies</b>.
            </p>
            </div>
        """, unsafe_allow_html=True)

    adv_mode = st.checkbox("🔍 Enable Advanced Comparison", value=False)

    # Dynamically handle wind column
    wind_col = "wind_kph" if "wind_kph" in df_trend_filtered.columns else "wind_mph"

    # Update the factors list
    factors = ["temperature_celsius", "humidity", wind_col, "uv_index", "precip_mm", "pressure_mb"]

    # Axis selection logic
    if adv_mode:
        x_axis = st.selectbox("Select X-axis Feature", factors, index=0)
        y_axis = st.selectbox("Select Y-axis Feature", factors, index=1)
    else:
        x_axis, y_axis = "temperature_celsius", "humidity"

    # Create scatter plot
    fig_feat = px.scatter(
        df_trend_filtered,
        x=x_axis,
        y=y_axis,
        color="condition_text",
        size="uv_index" if "uv_index" in df_trend_filtered.columns else None,
        hover_data=[
            "country",
            "location_name",
            "temperature_celsius",
            "humidity",
            wind_col,
            "uv_index",
        ],
        title=f"{x_axis.replace('_',' ').title()} vs {y_axis.replace('_',' ').title()} by Weather Condition",
    )

    st.plotly_chart(fig_feat, use_container_width=True)


    # ============================
    # 📋 Data Sample (Essential Columns)
    # ============================
    styled_header("📋 Filtered Data Sample")

    display_columns = [
        "continent", "country", "location_name", "condition_text",
        "temperature_celsius", "humidity", "precip_mm", "uv_index",
        "wind_kph", "last_updated" if "last_updated" in df_filtered.columns else "date",
        "Year", "Month", "Day",
    ]
    display_columns = [col for col in display_columns if col in df_filtered.columns]

    st.dataframe(
        df_filtered[display_columns].sample(min(100, len(df_filtered))),
        use_container_width=True,
    )
