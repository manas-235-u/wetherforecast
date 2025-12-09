from datetime import datetime

from astral import LocationInfo
from astral.sun import sun


class SunTimes:
    def get(self, city: str, lat: float, lon: float):
        # Create location
        loc = LocationInfo(
            name=city,
            region="India",
            timezone="Asia/Kolkata",
            latitude=lat,
            longitude=lon,
        )

        # ✅ CORRECT ORDER: observer first, then date and tzinfo as keyword args
        s = sun(
            loc.observer,
            date=datetime.now(),
            tzinfo=loc.timezone,
        )

        # Return simple dict
        return {
            "sunrise": s["sunrise"],
            "sunset": s["sunset"],
            "dawn": s["dawn"],
            "dusk": s["dusk"],
        }
