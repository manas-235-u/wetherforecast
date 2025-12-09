import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from models.sun_times import SunTimes

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Weather Forecast",
    page_icon="⛅",
    layout="wide",
)

# =========================
# GLOBAL CSS (BLUE DASHBOARD)
# =========================
APP_STYLE = """
<style>
.stApp {
    background: radial-gradient(circle at top, #38bdf8 0%, #1d4ed8 35%, #0f172a 80%);
    color: #e5e7eb;
    font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    max-width: 1100px;
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
}

/* Hero card (big temperature + city) */
.hero-card {
    border-radius: 22px;
    padding: 20px 24px;
    background: linear-gradient(145deg, rgba(15,23,42,0.85), rgba(37,99,235,0.95));
    box-shadow: 0 22px 45px rgba(0,0,0,0.45);
    border: 1px solid rgba(148,163,184,0.5);
    backdrop-filter: blur(18px);
}

.hero-temp {
    font-size: 3.6rem;
    font-weight: 700;
    line-height: 1;
    color: #f9fafb;
    margin-bottom: 0.2rem;
}

.hero-city {
    font-size: 1.6rem;
    font-weight: 600;
    color: #e5e7eb;
}

.hero-sub {
    font-size: 0.9rem;
    color: #cbd5f5;
    margin-top: 0.25rem;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(148,163,184,0.7);
    font-size: 0.78rem;
    color: #e5e7eb;
    margin-top: 0.6rem;
}

/* Metric cards */
.weather-card {
    border-radius: 14px;
    padding: 0.7rem 0.8rem;
    margin-bottom: 0.7rem;
    border: 1px solid rgba(148,163,184,0.45);
    background: rgba(15,23,42,0.82);
    box-shadow: 0 16px 36px rgba(0,0,0,0.4);
    text-align: left;
    color: #e5e7eb;
    backdrop-filter: blur(16px);
}
.weather-card h4 {
    margin-bottom: 0.15rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
}
.weather-card p {
    margin: 0;
    font-size: 1.0rem;
}

/* Hourly forecast cards */
.forecast-card {
    border-radius: 12px;
    padding: 0.55rem 0.7rem;
    margin-bottom: 0.6rem;
    border: 1px solid rgba(148,163,184,0.35);
    background: rgba(15,23,42,0.78);
    font-size: 0.85rem;
    box-shadow: 0 14px 30px rgba(0,0,0,0.35);
    backdrop-filter: blur(12px);
    color: #e5e7eb;
}

/* Titles */
h1 {
    color: #f9fafb;
}
.small-caption {
    font-size: 0.85rem;
    color: #d1d5db;
}

/* Fix text input label color */
label {
    color: #e5e7eb !important;
}
</style>
"""
st.markdown(APP_STYLE, unsafe_allow_html=True)

# =========================
# DATA FETCHING HELPERS
# =========================
def geocode_city(city: str):
    """
    Use Open-Meteo geocoding API to get latitude, longitude and timezone.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    res = data["results"][0]
    return {
        "name": res.get("name", city),
        "lat": res["latitude"],
        "lon": res["longitude"],
        "timezone": res.get("timezone", "UTC"),
        "country": res.get("country", ""),
    }


def fetch_weather(lat: float, lon: float, timezone: str):
    """
    Fetch current & hourly weather from Open-Meteo.
    Returns (current_weather_dict, hourly_df)
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,pressure_msl,cloud_cover,visibility",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": timezone,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    # ----- current weather -----
    current = data.get("current", {})
    temp = current.get("temperature_2m")
    feels_like = current.get("apparent_temperature")
    humidity = current.get("relative_humidity_2m")
    wind_speed = current.get("wind_speed_10m")
    pressure = current.get("pressure_msl")
    clouds = current.get("cloud_cover")
    visibility = current.get("visibility")

    current_weather = {
        "temp": temp,
        "feels_like": feels_like,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "clouds": clouds,
        "visibility": visibility,
        "description": "Cloudy" if clouds and clouds > 50 else "Clear",
    }

    # ----- hourly forecast -----
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    hums = hourly.get("relative_humidity_2m", [])
    winds = hourly.get("wind_speed_10m", [])

    if not times:
        hourly_df = pd.DataFrame()
    else:
        hourly_df = pd.DataFrame(
            {
                "time": times,
                "temp": temps,
                "humidity": hums,
                "wind_speed": winds,
            }
        )
        hourly_df = hourly_df.head(8)

    return current_weather, hourly_df


# =========================
# UI HELPERS (CARDS)
# =========================
def show_current_weather_cards(
    current_weather: dict,
    sun_info: dict | None = None,
    city_name: str | None = None,
    timezone_str: str | None = None,
):
    temp = current_weather.get("temp")
    feels_like = current_weather.get("feels_like")
    wind_speed = current_weather.get("wind_speed")
    humidity = current_weather.get("humidity")
    pressure = current_weather.get("pressure")
    description = current_weather.get("description", "").title()
    visibility = current_weather.get("visibility")
    clouds = current_weather.get("clouds")

    sunrise = sun_info.get("sunrise") if sun_info else None
    sunset = sun_info.get("sunset") if sun_info else None

    # Hero (big) card
    now_str = datetime.now().strftime("%I:%M %p · %A, %d %b %Y")
    city_label = city_name or "Selected location"

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-temp">{temp:.1f}°C</div>
            <div class="hero-city">{city_label}</div>
            <div class="hero-sub">{now_str}</div>
            <div class="hero-pill">Feels like {feels_like:.1f}°C · {description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    st.markdown("#### Current details", unsafe_allow_html=True)
    st.markdown(
        "<p class='small-caption'>Key conditions right now at this location.</p>",
        unsafe_allow_html=True,
    )

    # Row 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="weather-card">
                <h4>Wind Speed</h4>
                <p><b>{wind_speed:.1f} km/h</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="weather-card">
                <h4>Humidity</h4>
                <p><b>{humidity:.0f} %</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="weather-card">
                <h4>Pressure</h4>
                <p><b>{pressure:.0f} hPa</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Row 2
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        if visibility is not None:
            st.markdown(
                f"""
                <div class="weather-card">
                    <h4>Visibility</h4>
                    <p><b>{visibility:.0f} m</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col5:
        if clouds is not None:
            st.markdown(
                f"""
                <div class="weather-card">
                    <h4>Cloud Cover</h4>
                    <p><b>{clouds:.0f} %</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col6:
        if sunrise:
            if isinstance(sunrise, datetime):
                sunrise_str = sunrise.strftime("%H:%M")
            else:
                sunrise_str = str(sunrise)
            st.markdown(
                f"""
                <div class="weather-card">
                    <h4>Sunrise</h4>
                    <p><b>{sunrise_str}</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col7:
        if sunset:
            if isinstance(sunset, datetime):
                sunset_str = sunset.strftime("%H:%M")
            else:
                sunset_str = str(sunset)
            st.markdown(
                f"""
                <div class="weather-card">
                    <h4>Sunset</h4>
                    <p><b>{sunset_str}</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def show_hourly_forecast_cards(hourly_df: pd.DataFrame):
    st.markdown("#### Next hours forecast", unsafe_allow_html=True)
    st.markdown(
        "<p class='small-caption'>Short-term outlook in compact cards.</p>",
        unsafe_allow_html=True,
    )

    if hourly_df is None or hourly_df.empty:
        st.info("No hourly forecast available.")
        return

    cols = st.columns(2)
    for i, (_, row) in enumerate(hourly_df.iterrows()):
        col = cols[i % 2]
        with col:
            t_raw = row["time"]
            try:
                t = datetime.fromisoformat(t_raw)
                t_str = t.strftime("%d %b · %H:%M")
            except Exception:
                t_str = str(t_raw)

            temp = row["temp"]
            wind = row["wind_speed"]
            hum = row["humidity"]

            st.markdown(
                f"""
                <div class="forecast-card">
                    <b>{t_str}</b><br/>
                    Temp: {temp:.1f} °C<br/>
                    Wind: {wind:.1f} km/h<br/>
                    Humidity: {hum:.0f} %
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================
# MAIN STREAMLIT APP
# =========================
def main():
    st.title("⛅ Weatherboard")
    st.markdown(
        "<p class='small-caption'>Search any city worldwide to see a clean, card-based weather view.</p>",
        unsafe_allow_html=True,
    )

    city = st.text_input("City", value="Bhubaneswar")

    if st.button("Get Weather"):
        if not city.strip():
            st.error("Enter a valid city name.")
            return

        with st.spinner("Finding location..."):
            geo = geocode_city(city.strip())

        if geo is None:
            st.error("Could not find that city. Try another name.")
            return

        lat = geo["lat"]
        lon = geo["lon"]
        timezone = geo["timezone"]

        st.success(f"Location: {geo['name']}, {geo['country']} (lat: {lat:.2f}, lon: {lon:.2f})")

        sun = SunTimes().get(geo["name"], lat, lon)

        with st.spinner("Fetching weather..."):
            current_weather, hourly_df = fetch_weather(lat, lon, timezone)

        # Layout: left = hero + metrics, right = hourly forecast
        left, right = st.columns([1.6, 1.4], gap="large")

        with left:
            show_current_weather_cards(
                current_weather,
                sun_info=sun,
                city_name=geo["name"],
                timezone_str=timezone,
            )

        with right:
            show_hourly_forecast_cards(hourly_df)


if __name__ == "__main__":
    main()
