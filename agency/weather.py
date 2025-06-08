from langchain_core.tools import Tool
from pydantic import BaseModel
import requests

class WeatherInput(BaseModel):
    location: str

def get_weather_by_location(location: str) -> str:
    """Returns current weather conditions for a specified city or location."""
    geo_response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": location, "format": "json"},
        headers={"User-Agent": "MyApp/1.0 (contact@example.com)"}
    )
    geo_results = geo_response.json()
    if not geo_results:
        raise ValueError(f"Location '{location}' not found.")
    latitude = geo_results[0]["lat"]
    longitude = geo_results[0]["lon"]

    weather_response = requests.get(
        f"https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "cloud_cover,wind_speed_10m,wind_direction_10m,temperature_2m,relative_humidity_2m,is_day,rain",
        }
    )
    weather_data = weather_response.json()
    current_weather = weather_data.get("current", "No weather data available.")
    return str(current_weather)

get_weather_tool = Tool(
    name="get_weather_by_location",
    func=get_weather_by_location,
    description=(
        "Returns current weather conditions for a specified city or location.\n"
        "Input: { location: string } — e.g., { location: 'New York' }.\n"
        "Output: JSON string with keys like 'temperature', 'humidity', 'wind_speed', etc.\n"
    ),
    args_schema=WeatherInput
)