from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

DATE_TIME_FORMAT = "%d-%m-%Y %H:%M:%S"

class DateTimeRequest(BaseModel):
    utc_offset: int = Field(
        default=0,
        description="Timezone offset in hours for current date and time"
    )

def datetime_now(request: DateTimeRequest) -> str:
    try:
        tz = timezone(timedelta(hours=request.utc_offset))
        now = datetime.now(tz)
        formatted_time = now.strftime(DATE_TIME_FORMAT)
        return formatted_time
    except Exception as error:
        return f"Error getting current date/time: {str(error)}"