from datetime import datetime, date, timedelta
from typing import Dict, Optional


def get_dates_info(include_week_start: bool = True, include_month_start: bool = True) -> Dict[str, str]:
    """
    Returns a dictionary with useful date information:
    - 'today': Today's date (YYYY-MM-DD)
    - 'month_end': Last date of the current month (YYYY-MM-DD)
    - 'week_end': Last date of the current week (Sunday) (YYYY-MM-DD)
    - 'month_start': First date of the current month (YYYY-MM-DD)
    - 'week_start': First date of the current week (Monday) (YYYY-MM-DD)
    - 'month_str': Current month in 'Mon-YYYY' format (e.g. Apr-2025)

    Args:
        include_week_start (bool): If True, includes the start of the week (Monday).
        include_month_start (bool): If True, includes the start of the month.

    Returns:
        dict: A dictionary with formatted date strings.
    """
    today = date.today()

    # End of month calculation
    next_month = today.replace(day=28) + timedelta(days=4)  # This will give us the first day of next month
    month_end = next_month - timedelta(days=next_month.day)  # Subtract days to get the last day of current month

    # Start of month (first day of the current month)
    month_start = today.replace(day=1)

    # End of week (Sunday)
    days_until_sunday = 6 - today.weekday()
    week_end = today + timedelta(days=days_until_sunday)

    # Start of week (Monday)
    days_since_monday = today.weekday()  # Monday is 0, Sunday is 6
    week_start = today - timedelta(days=days_since_monday)

    # Return dictionary with all required info
    dates_info = {
        "today": today.strftime("%Y-%m-%d"),
        "month_end": month_end.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"),
        "month_str": today.strftime("%b-%Y"),
    }

    if include_week_start:
        dates_info["week_start"] = week_start.strftime("%Y-%m-%d")
    if include_month_start:
        dates_info["month_start"] = month_start.strftime("%Y-%m-%d")

    return dates_info


def get_relative_dates(days_from_today: int) -> Dict[str, str]:
    """
    Returns a dictionary with relative date calculations from 'today' by adding/subtracting the provided number of days.

    Args:
        days_from_today (int): Number of days to add/subtract from today's date.

    Returns:
        dict: A dictionary with the relative date (YYYY-MM-DD).

    Example:
        >>> get_relative_dates(5)
        {'relative_date': '2025-05-03'}
    """
    today = date.today()
    relative_date = today + timedelta(days=days_from_today)
    return {"relative_date": relative_date.strftime("%Y-%m-%d")}


def get_date_range_info(date_range: str, date_format: str = "%d %B %Y") -> Optional[Dict[str, str]]:
    """
    Extracts the start and end dates from a date range string and returns them in 'YYYYMMDD' format.

    Args:
        date_range (str): A string containing a date range in the format
                          'DD Month YYYY – DD Month YYYY'.
        date_format (str): The format to parse the date range. Default is '%d %B %Y'.

    Returns:
        dict: A dictionary with 'start_date' and 'end_date' in 'YYYYMMDD' format, or None if invalid.

    Example:
        >>> get_date_range_info("01 January 2025 – 31 January 2025")
        {'start_date': '20250101', 'end_date': '20250131'}
    """
    try:
        start_date_str, end_date_str = date_range.split("–")
        start_date_str = start_date_str.strip()
        end_date_str = end_date_str.strip()

        start_date = datetime.strptime(start_date_str, date_format)
        end_date = datetime.strptime(end_date_str, date_format)

        return {
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d")
        }
    except ValueError:
        return None
