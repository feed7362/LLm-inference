from datetime import datetime, timezone, timedelta
from langchain_core.tools import Tool
from pydantic import BaseModel

DATE_TIME_FORMAT = "%d-%m-%Y %H:%M:%S"

@tool
def datetime_now(utc_offset: int = 0) -> str:
    """
    Returns the current date and time with an optional UTC offset in hours.
    """
    try:
        tz = timezone(timedelta(hours=utc_offset))
        now = datetime.now(tz)
        return now.strftime(DATE_TIME_FORMAT)
    except Exception as error:
        return f"Error getting current date/time: {str(error)}"

datetime_tool = Tool(
    name="datetime_now",
    func=datetime_now,
    description=(
        "Returns the current date and time with an optional UTC offset in hours.\n"
        "Input: { utc_offset: int } — e.g., { utc_offset: 3 }\n"
        f"Output: Formatted datetime string in '{DATE_TIME_FORMAT}' format.\n"
    )
)
