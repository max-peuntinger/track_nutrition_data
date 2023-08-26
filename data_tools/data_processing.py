from datetime import datetime
import pandas as pd
import pytz
from typing import Dict, Optional
from decorators import log_execution_time


@log_execution_time
def process_nutrition_data(
    weight: float, nutrition_data: Dict[str, any], timestamp: Optional[str] = None
) -> Dict[str, any]:
    """Processes nutrition data by multiplying the values by the given weight and adding a timestamp.

    Args:
        weight (float): The weight to multiply the nutrition values by.
        nutrition_data (dict): The nutrition data to process.
        timestamp (str, optional): The timestamp to use. If not provided, the current time in the Berlin timezone is used.

    Returns:
        dict: The processed nutrition data, including the timestamp and adjusted values.
    """
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
    """Categorizes the given time into a time-of-day category.
    Attention: The timeframe from 00:00-02:00 still counts as the previous day to align the definiton of a day with my sleeping/eating patterns.

    Args:
        t (datetime): The time to categorize.

    Returns:
        str: A string representing the time-of-day category, such as "2-12" or "17-22".
    """
    if 2 <= t.hour < 12:
        return "2-12"
    elif 12 <= t.hour < 17:
        return "12-17"
    elif 17 <= t.hour < 22:
        return "17-22"
    else:
        return "22-2"  # now this includes 00:00 to 02:00 as it is part of the previous day for my day/night cycle


@log_execution_time
def filter_data_by_date(
    df: pd.DataFrame, start_date: Optional[datetime], end_date: Optional[datetime]
) -> pd.DataFrame:
    """Filters a DataFrame by date, keeping only the rows between the given start and end dates.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        start_date (datetime, optional): The start date of the filter. If not provided, no filtering is done on the start date.
        end_date (datetime, optional): The end date of the filter. If not provided, no filtering is done on the end date.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    return df
