from datetime import datetime

from astral import LocationInfo
from astral.moon import moonrise, moonset


class MoonTimes:
    def get(self, city: str, lat: float, lon: float):
        # Build location object
        loc = LocationInfo(
            name=city,
            region="India",
            timezone="Asia/Kolkata",
            latitude=lat,
            longitude=lon,
        )

        now = datetime.now()

        # Correct usage: observer first, then date/tzinfo
        mr = moonrise(
            loc.observer,
            date=now,
            tzinfo=loc.timezone,
        )

        ms = moonset(
            loc.observer,
            date=now,
            tzinfo=loc.timezone,
        )

        return {
            "moonrise": mr,
            "moonset": ms,
        }
