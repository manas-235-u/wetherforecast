import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math

CITY_COORDS = {
    "madrid": (40.4, -3.7),
    "delhi": (28.6, 77.2),
    "bhubaneswar": (20.29, 85.82),
    "london": (51.50, -0.12),
    "new york": (40.71, -74.00),
    "tokyo": (35.67, 139.65),
}

def generate_synthetic_weather(days=120):
    rows = []
    base = datetime(2024, 1, 1)
    rng = np.random.default_rng(42)

    for city, (lat, lon) in CITY_COORDS.items():
        for d in range(days):
            for hour in range(24):
                
                dt = base + timedelta(days=d, hours=hour)
                day_of_year = dt.timetuple().tm_yday

                # Temperature
                seasonal = 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
                diurnal = 6 * np.sin(2 * np.pi * (hour - 14) / 24)
                temp = 20 + seasonal + diurnal + rng.normal(0, 1.5)

                # Humidity
                humidity = 60 + rng.normal(0, 8) - 0.2 * diurnal

                # Wind Speed / Direction
                wind_speed = abs(rng.normal(6, 2))
                wind_dir = rng.integers(0, 360)

                # AQI
                aqi = (
                    60
                    + 0.4 * temp
                    + 0.3 * humidity
                    - 0.5 * wind_speed
                    + rng.normal(0, 5)
                )

                # UV
                uv = max(0, 10 * math.sin((hour / 24) * np.pi))

                # Visibility
                visibility = max(1, 10 - (humidity - 50) * 0.05 + rng.normal(0, 0.5))

                # Pressure
                pressure = 1005 + 5 * np.sin(d / 10) + rng.normal(0, 1)

                rows.append(
                    {
                        "city": city,
                        "datetime": dt,
                        "lat": lat,
                        "lon": lon,
                        "day_of_year": day_of_year,
                        "hour": hour,
                        "temp": temp,
                        "humidity": humidity,
                        "wind_speed": wind_speed,
                        "wind_dir": wind_dir,
                        "aqi": aqi,
                        "uv": uv,
                        "visibility": visibility,
                        "pressure": pressure,
                    }
                )

    df = pd.DataFrame(rows)
    return df
