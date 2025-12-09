

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

import pandas as pd
import requests


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


class WeatherAPIError(RuntimeError):
    """Custom exception for weather API failures."""
    pass


@dataclass
class WeatherAPI:
    """Client for Open-Meteo weather + air-quality APIs."""

    def get_daily_forecast(self, lat: float, lon: float, days: int = 3) -> pd.DataFrame:
        if days <= 0:
            raise ValueError("days must be >= 1")
        if days > 16:
            days = 16

        params: Dict[str, Any] = {
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                    "wind_direction_10m_dominant",
                    "uv_index_max",
                ]
            ),
            "timezone": "auto",
            "forecast_days": days,
        }

        resp = requests.get(FORECAST_URL, params=params, timeout=10)
        if not resp.ok:
            raise WeatherAPIError(f"Forecast API error: {resp.status_code} {resp.text[:150]}")

        data = resp.json()
        if "daily" not in data:
            raise WeatherAPIError("No 'daily' section found in API response")

        daily = data["daily"]

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(daily["time"]),
                "temp_max": daily["temperature_2m_max"],
                "temp_min": daily["temperature_2m_min"],
                "feels_like_max": daily["apparent_temperature_max"],
                "feels_like_min": daily["apparent_temperature_min"],
                "precipitation_mm": daily["precipitation_sum"],
                "rain_probability": daily["precipitation_probability_max"],
                "wind_speed_max": daily["wind_speed_10m_max"],
                "wind_direction": daily["wind_direction_10m_dominant"],
                "uv_index_max": daily["uv_index_max"],
            }
        )

        df["temp_mean"] = (df["temp_max"] + df["temp_min"]) / 2
        return df

    def get_current_air_quality(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "european_aqi,pm10,pm2_5",
            "timezone": "auto",
        }

        resp = requests.get(AIR_QUALITY_URL, params=params, timeout=10)
        if not resp.ok:
            return None

        data = resp.json()
        if "hourly" not in data:
            return None

        hourly = data["hourly"]
        times = hourly.get("time")
        if not times:
            return None

        idx = len(times) - 1

        return {
            "time": pd.to_datetime(times[idx]),
            "aqi": hourly.get("european_aqi", [None])[idx],
            "pm10": hourly.get("pm10", [None])[idx],
            "pm2_5": hourly.get("pm2_5", [None])[idx],
        }
