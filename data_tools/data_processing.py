from datetime import datetime
import pandas as pd
import pytz
from typing import Optional


def process_nutrition_data(weight, nutrition_data, timestamp=None):
    data = {}
    if not timestamp:
        berlin_tz = pytz.timezone("Europe/Berlin")
        berlin_time = datetime.now(berlin_tz)
        data["timestamp"] = berlin_time.isoformat()
    else:
        data["timestamp"] = timestamp
    for key, value in nutrition_data["items"][0].items():
        if key == "name":
            data[key] = value
            continue
        data[key] = float(value) * float(weight) / 100.0
    return data


def time_of_day(t: datetime) -> str:
        # Define function to categorize time of day
        if 2 <= t.hour < 12:
            return "2-12"
        elif 12 <= t.hour < 17:
            return "12-17"
        elif 17 <= t.hour < 22:
            return "17-22"
        else:
            return "22-2"  # now this includes 00:00 to 02:00 as it is part of the previous day for my day/night cycle
        

def filter_data_by_date(
    df: pd.DataFrame, start_date: Optional[datetime], end_date: Optional[datetime]
) -> pd.DataFrame:
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    return df
