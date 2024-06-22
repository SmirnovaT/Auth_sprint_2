import calendar
import datetime as dt
from datetime import datetime, timedelta
from typing import Tuple


async def calculate_current_date_and_time() -> Tuple[dt, int]:
    """Calculates current date and time"""

    current_date_and_time_datetime = datetime.now(dt.timezone.utc)
    current_date_and_time_timestamp = int(
        calendar.timegm(current_date_and_time_datetime.timetuple())
    )

    return current_date_and_time_datetime, current_date_and_time_timestamp


async def calculate_iat_and_exp_tokens() -> Tuple[int, int, int]:
    """
    Calculates 'iat' and 'exp' for access and refresh tokens
    """
    current_date_and_time_datetime, iat_timestamp = (
        await calculate_current_date_and_time()
    )

    exp_access_token = current_date_and_time_datetime + timedelta(minutes=15)
    exp_refresh_token = current_date_and_time_datetime + timedelta(days=10)

    exp_access_token_timestamp = int(calendar.timegm(exp_access_token.timetuple()))
    exp_refresh_token_timestamp = int(calendar.timegm(exp_refresh_token.timetuple()))

    return iat_timestamp, exp_access_token_timestamp, exp_refresh_token_timestamp
