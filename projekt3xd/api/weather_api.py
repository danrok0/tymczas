import requests
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from functools import reduce
from config import OPEN_METEO_API, CITY_COORDINATES

class WeatherAPI:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        self.forecast_url = f"{self.base_url}/forecast"
        self.history_url = f"{self.base_url}/archive"
        self.visual_crossing_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        self.visual_crossing_api_key = "YOUR_API_KEY"  # Należy zastąpić prawdziwym kluczem API
        self.openweather_url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        self.openweather_api_key = "YOUR_API_KEY"  # Należy zastąpić prawdziwym kluczem API
        self.worldweather_url = "http://api.worldweatheronline.com/premium/v1/past-weather.ashx"
        self.worldweather_api_key = "YOUR_API_KEY"  # Należy zastąpić prawdziwym kluczem API
        self.weather_data_file = "api/weather_data.json"

    def _calculate_average_temperature(self, daily_data: Dict[str, List[float]]) -> float:
        """Calculate average temperature using reduce."""
        temps = [daily_data.get("temperature_2m_max", [0])[0], 
                daily_data.get("temperature_2m_min", [0])[0]]
        return reduce(lambda x, y: x + y, temps) / len(temps)

    def _process_weather_data(self, data: Dict[str, Any], city: str, date: str) -> Dict[str, Any]:
        """Process weather data using dictionary comprehension."""
        daily_data = data.get("daily", {})
        
        # Use dictionary comprehension to create weather data
        weather_data = {
            "date": date,
            "region": city,
            "temperature_min": daily_data.get("temperature_2m_min", [0])[0],
            "temperature_max": daily_data.get("temperature_2m_max", [0])[0],
            "temperature_avg": self._calculate_average_temperature(daily_data),
            "precipitation": daily_data.get("precipitation_sum", [0])[0],
            "cloud_cover": daily_data.get("cloudcover_mean", [0])[0],
            "wind_speed": daily_data.get("windspeed_10m_max", [0])[0],
            "sunshine_hours": daily_data.get("sunshine_duration", [0])[0] / 3600
        }
        
        return weather_data

    def get_weather_forecast(self, city: str, date: str) -> Optional[Dict[str, Any]]:
        """Get weather forecast for a specific date."""
        try:
            # Convert date string to datetime
            target_date = datetime.strptime(date, "%Y-%m-%d")
            today = datetime.now().date()
            
            # Choose appropriate API endpoint based on date
            if target_date.date() < today:
                print(f"Pobieranie historycznych danych pogodowych dla {city} na dzień {date}...")
                return self._get_historical_weather(city, date)
            else:
                print(f"Pobieranie prognozy pogody dla {city} na dzień {date}...")
                return self._get_future_weather(city, date)
                
        except Exception as e:
            print(f"Błąd podczas pobierania danych pogodowych: {e}")
            return None

    def _get_future_weather(self, city: str, date: str) -> Optional[Dict[str, Any]]:
        """Get weather forecast for future dates."""
        try:
            # Get coordinates for the city
            coordinates = self._get_city_coordinates(city)
            if not coordinates:
                return None

            # Prepare parameters for the API request
            params = {
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"],
                "start_date": date,
                "end_date": date,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "sunshine_duration",
                    "cloudcover_mean",
                    "windspeed_10m_max",
                    "winddirection_10m_dominant"
                ],
                "timezone": "Europe/Warsaw"
            }

            # Make the API request
            response = requests.get(self.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract and format the weather data
            daily = data["daily"]
            return {
                "temperature_max": daily["temperature_2m_max"][0],
                "temperature_min": daily["temperature_2m_min"][0],
                "temperature_avg": (daily["temperature_2m_max"][0] + daily["temperature_2m_min"][0]) / 2,
                "precipitation": daily["precipitation_sum"][0],
                "sunshine_hours": daily["sunshine_duration"][0] / 3600,  # Convert seconds to hours
                "cloud_cover": daily["cloudcover_mean"][0],
                "wind_speed": daily["windspeed_10m_max"][0]
            }

        except Exception as e:
            print(f"Błąd podczas pobierania prognozy pogody: {e}")
            return None

    def _get_historical_weather(self, city: str, date: str) -> Optional[Dict[str, Any]]:
        """Get historical weather data from local JSON file."""
        try:
            # Load weather data from file
            with open(self.weather_data_file, 'r', encoding='utf-8') as f:
                weather_data = json.load(f)

            # Check if we have data for this city and date
            if city in weather_data and date in weather_data[city]:
                return weather_data[city][date]
            else:
                # If no exact match, return average values for the city
                if city in weather_data:
                    city_data = weather_data[city]
                    dates = list(city_data.keys())
                    if dates:
                        # Return data from the first available date
                        return city_data[dates[0]]
                
                print(f"Brak danych historycznych dla {city} na dzień {date}")
                return None

        except Exception as e:
            print(f"Błąd podczas pobierania historycznych danych pogodowych: {e}")
            return None

    def _get_city_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a given city."""
        city_coordinates = {
            "Gdańsk": {"latitude": 54.3520, "longitude": 18.6466},
            "Warszawa": {"latitude": 52.2297, "longitude": 21.0122},
            "Kraków": {"latitude": 50.0647, "longitude": 19.9450},
            "Wrocław": {"latitude": 51.1079, "longitude": 17.0385}
        }
        return city_coordinates.get(city)

    def get_weather_for_date_range(self, city: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get weather for a date range using map."""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Generate list of dates
            date_list = [start + timedelta(days=x) for x in range((end - start).days + 1)]
            
            # Use map to get weather for each date
            weather_data = list(map(
                lambda date: self.get_weather_forecast(city, date.strftime("%Y-%m-%d")),
                date_list
            ))
            
            # Filter out None values
            return list(filter(None, weather_data))
            
        except ValueError as e:
            print(f"Nieprawidłowy format daty: {e}")
            return [] 