from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

class DateTimeRequest(BaseModel):
    utc: int = Field(description="Get current date and time by UTC", default=0)

def datetime_now(request: DateTimeRequest) -> str:
    try:
        tz = timezone(timedelta(hours=request.utc))
        now = datetime.now(tz)
        return now.strftime("%d-%m-%Y %H:%M:%S")
    except Exception as e:
        return f"Error getting current date/time: {str(e)}"