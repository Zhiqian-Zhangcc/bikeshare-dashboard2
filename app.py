"""CityRide operations dashboard built from the Capital Bikeshare hourly snapshot."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(layout="wide", page_title="CityRide Operations Center")

SEASON_MAP = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHER_MAP = {
    1: "Clear",
    2: "Mist/Cloudy",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Snow",
}
DAY_TYPE_MAP = {1: "Working day", 0: "Weekend/Holiday"}
SEASON_ORDER = list(SEASON_MAP.values())
WEATHER_ORDER = list(WEATHER_MAP.values())
DAY_TYPE_ORDER = ["Working day", "Weekend/Holiday"]


@st.cache_data
def load_data() -> pd.DataFrame:
    """Read the local hourly file once and add readable categorical labels."""
    data_path = Path(__file__).parent / "hour.csv"
    data = pd.read_csv(data_path)
    data["year"] = data["yr"] + 2011
    data["season_label"] = data["season"].map(SEASON_MAP)
    data["weather_label"] = data["weathersit"].map(WEATHER_MAP)
    data["day_type"] = data["workingday"].map(DAY_TYPE_MAP)
    return data


def reset_filters() -> None:
    """Restore every sidebar control to its all-data default."""
    st.session_state.year_filter = [2011, 2012]
    st.session_state.season_filter = SEASON_ORDER.copy()
    st.session_state.day_type_filter = DAY_TYPE_ORDER.copy()
    st.session_state.weather_filter = WEATHER_ORDER.copy()


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Return only the rows selected through the sidebar controls."""
    return data[
        data["year"].isin(st.session_state.year_filter)
        & data["season_label"].isin(st.session_state.season_filter)
        & data["day_type"].isin(st.session_state.day_type_filter)
        & data["weather_label"].isin(st.session_state.weather_filter)
    ].copy()


st.markdown(
    """
    <style>
        .stApp { background: #101722; color: #e8eef7; }
        [data-testid="stSidebar"] { background: #172131; }
        [data-testid="stMetric"] {
            background: #1b2738; border: 1px solid #2d425b; border-radius: 10px;
            padding: 16px;
        }
        h1, h2, h3 { color: #f4f8fc; }
        .data-note { color: #aab9ca; font-size: 0.92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

data = load_data()

st.title("CityRide Shared Bike Operations Command Center")
st.caption(
    "For the shared-bike operations manager: plan vehicle rebalancing and maintenance around hourly demand."
)
st.markdown(
    '<p class="data-note">Data: 2011–2012 Kaggle historical snapshot | Intended production refresh: hourly</p>',
    unsafe_allow_html=True,
)

st.sidebar.header("Operations filters")
st.sidebar.multiselect("Year", [2011, 2012], default=[2011, 2012], key="year_filter")
st.sidebar.multiselect("Season", SEASON_ORDER, default=SEASON_ORDER, key="season_filter")
st.sidebar.multiselect("Day type", DAY_TYPE_ORDER, default=DAY_TYPE_ORDER, key="day_type_filter")
st.sidebar.multiselect("Weather", WEATHER_ORDER, default=WEATHER_ORDER, key="weather_filter")
st.sidebar.button("Reset filters", on_click=reset_filters, use_container_width=True)

filtered = apply_filters(data)

if filtered.empty:
    st.warning("No records match the current filters. Adjust a filter or select Reset filters.")
    st.stop()

# KPI values always follow the current selection.
hourly = filtered.groupby("hr", as_index=False)["cnt"].mean()
peak_hour = int(hourly.loc[hourly["cnt"].idxmax(), "hr"])
registered_share = filtered["registered"].sum() / filtered["cnt"].sum()

kpi_total, kpi_peak, kpi_registered = st.columns(3)
kpi_total.metric("Total rides", f"{filtered['cnt'].sum():,}")
kpi_peak.metric("Peak demand hour", f"{peak_hour:02d}:00")
kpi_registered.metric("Registered rider share", f"{registered_share:.1%}")

st.divider()
chart_left, chart_right = st.columns(2)

with chart_left:
    fig, ax = plt.subplots(figsize=(8, 4.6))
    selected_day_types = [item for item in DAY_TYPE_ORDER if item in st.session_state.day_type_filter]
    colors = {"Working day": "#4ea5ff", "Weekend/Holiday": "#4fd1a5"}
    if len(selected_day_types) > 1:
        profile = filtered.groupby(["hr", "day_type"], as_index=False)["cnt"].mean()
        for day_type in selected_day_types:
            subset = profile[profile["day_type"] == day_type]
            ax.plot(subset["hr"], subset["cnt"], marker="o", linewidth=2.2,
                    color=colors[day_type], label=day_type)
        ax.legend(title="Day type")
    else:
        ax.plot(hourly["hr"], hourly["cnt"], marker="o", linewidth=2.2, color="#4ea5ff")
    ax.set_title("Hourly demand profile", fontweight="bold")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Average total rides")
    ax.set_xticks(range(24))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

with chart_right:
    weather = filtered.groupby("weather_label")["cnt"].mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh(weather.index, weather.values, color="#f6ad55")
    ax.set_title("Demand by weather condition", fontweight="bold")
    ax.set_xlabel("Average total rides")
    ax.set_ylabel("Weather condition")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

# Create a concise recommendation from the selected data rather than a fixed statement.
chosen_day_types = set(st.session_state.day_type_filter)
if "Working day" in chosen_day_types and peak_hour >= 12:
    message = (
        f"Action: schedule rebalancing and maintenance capacity before {peak_hour:02d}:00, "
        "when the current selection reaches its highest average demand."
    )
else:
    message = (
        f"Action: position vehicles before {peak_hour:02d}:00, the highest-demand hour "
        "in the current filtered view."
    )
st.info(message)
