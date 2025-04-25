from pydantic import BaseModel, Field

class WeatherRequest(BaseModel):
    latitude: float = Field(description="Latitude of the location")
    longitude: float = Field(description="Longitude of the location")

def get_weather(request: WeatherRequest):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={request.latitude}&longitude={request.longitude}&current=cloud_cover,surface_pressure,wind_speed_10m,wind_direction_10m,temperature_2m,relative_humidity_2m,is_day,rain&past_hours=24")
    response.raise_for_status()
    return response.json()["current"]