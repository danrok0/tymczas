import json
from functools import reduce
from typing import List, Dict, Any
import os
import sys
from datetime import datetime

# Dodaj katalog projektu do ścieżki Pythona
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from api.trails_api import TrailsAPI
from api.weather_api import WeatherAPI
from config import CITY_COORDINATES

class TrailDataHandler:
    def __init__(self):
        self.api = TrailsAPI()
        self.weather_api = WeatherAPI()
        self.data_file = "api/trails_data.json"
        print("Pobieranie danych o szlakach z API...")
        self._update_trails_data()
        self.trails_data = self._load_trails_data()

    def _load_trails_data(self) -> List[Dict[str, Any]]:
        """Load trails data from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Błąd podczas wczytywania danych o trasach: {e}")
            return []

    def _update_trails_data(self):
        """Update trails data by fetching from API and saving to file."""
        print("Aktualizacja danych o szlakach...")
        all_trails = []
        
        # Get trails for all regions
        for region in CITY_COORDINATES.keys():
            print(f"\nPobieranie szlaków dla regionu: {region}")
            try:
                trails = self.api.get_hiking_trails(region)
                if trails:
                    all_trails.extend(trails)
                    print(f"Znaleziono {len(trails)} szlaków dla {region}")
            except Exception as e:
                print(f"Błąd podczas pobierania szlaków dla {region}: {e}")

        print(f"\nŁącznie znaleziono {len(all_trails)} szlaków")

        # Save to trails_data.json
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(all_trails, f, ensure_ascii=False, indent=2)
            print("Dane o szlakach zostały zapisane do pliku trails_data.json")
        except Exception as e:
            print(f"Błąd podczas zapisywania danych o szlakach: {e}")

    def _validate_trail(self, trail: Any) -> Dict[str, Any]:
        """Waliduje i formatuje dane szlaku."""
        if not isinstance(trail, dict):
            return None
            
        # Required fields with default values
        default_trail = {
            "id": "unknown",
            "name": "Unknown Trail",
            "region": "unknown",
            "length_km": 0.0,
            "difficulty": 1,
            "terrain_type": "mixed",
            "tags": []
        }
        
        # Update default values with actual data if valid
        if isinstance(trail, dict):
            for key in default_trail:
                if key in trail and trail[key] is not None:
                    default_trail[key] = trail[key]
                    
            # Ensure numeric fields are correct type
            try:
                default_trail["length_km"] = float(default_trail["length_km"])
                default_trail["difficulty"] = int(default_trail["difficulty"])
            except (ValueError, TypeError):
                default_trail["length_km"] = 0.0
                default_trail["difficulty"] = 1
                
        return default_trail

    def get_trails(self) -> List[Dict[str, Any]]:
        """Get all available trails."""
        all_trails = []
        for city in CITY_COORDINATES.keys():
            city_trails = self.get_trails_for_city(city)
            all_trails.extend(trail for trail in city_trails if trail is not None)
        return all_trails

    def get_trails_for_city(self, city: str) -> List[Dict[str, Any]]:
        """Get trails for a specific city from the data file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_trails = json.load(f)
                city_trails = [trail for trail in all_trails if trail.get("region", "").lower() == city.lower()]
                print(f"Znaleziono {len(city_trails)} szlaków dla miasta {city}")
                return city_trails
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Błąd podczas wczytywania danych o szlakach: {e}")
            return []

    def get_trail_by_id(self, trail_id: str) -> Dict[str, Any]:
        """Get a specific trail by its ID from the data file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_trails = json.load(f)
                for trail in all_trails:
                    if trail.get("id") == trail_id:
                        return trail
                return None
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Błąd podczas wczytywania danych o szlakach: {e}")
            return None

    def get_trails_by_difficulty(self, difficulty: int) -> List[Dict[str, Any]]:
        """Get trails with specific difficulty level from the data file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_trails = json.load(f)
                difficulty_trails = [trail for trail in all_trails if trail.get("difficulty") == difficulty]
                print(f"Znaleziono {len(difficulty_trails)} szlaków o trudności {difficulty}")
                return difficulty_trails
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Błąd podczas wczytywania danych o szlakach: {e}")
            return []

    def get_trails_by_terrain(self, terrain_type: str) -> List[Dict[str, Any]]:
        """Get trails with specific terrain type from the data file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_trails = json.load(f)
                terrain_trails = [trail for trail in all_trails if trail.get("terrain_type", "").lower() == terrain_type.lower()]
                print(f"Znaleziono {len(terrain_trails)} szlaków o typie terenu {terrain_type}")
                return terrain_trails
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Błąd podczas wczytywania danych o szlakach: {e}")
            return []

    def filter_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Filter trails by region."""
        return [trail for trail in self.get_trails() 
                if isinstance(trail, dict) and 
                trail.get('region', '').lower() == region.lower()]

    def filter_by_length(self, min_length: float, max_length: float) -> List[Dict[str, Any]]:
        """Filter trails by length range."""
        return [trail for trail in self.get_trails()
                if isinstance(trail, dict) and
                min_length <= trail.get('length_km', 0) <= max_length]

    def filter_by_difficulty(self, difficulty: int) -> List[Dict[str, Any]]:
        """Filter trails by difficulty level."""
        return [trail for trail in self.get_trails()
                if isinstance(trail, dict) and
                trail.get('difficulty') == difficulty]

    def get_average_length(self) -> float:
        """Calculate average length of all trails."""
        trails = [trail for trail in self.get_trails() if isinstance(trail, dict)]
        if not trails:
            return 0
        return sum(trail.get('length_km', 0) for trail in trails) / len(trails)

    def save_trails(self, filename: str):
        """Save all trails to a JSON file."""
        trails = [trail for trail in self.get_trails() if isinstance(trail, dict)]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(trails, f, ensure_ascii=False, indent=2)

    def get_trails_by_weather_conditions(self, city: str, date: str, 
                                       max_precipitation: float = None,
                                       min_temperature: float = None,
                                       max_temperature: float = None) -> List[Dict[str, Any]]:
        """Get trails filtered by weather conditions."""
        try:
            # Get weather forecast for the specified date
            weather = self.weather_api.get_weather_forecast(city, date)
            if not weather:
                print(f"Brak danych pogodowych dla {city} na dzień {date}")
                return []
            
            # Calculate hiking comfort index
            from utils.weather_utils import WeatherUtils
            comfort_index = WeatherUtils.calculate_hiking_comfort(weather)

            # Get all trails for the city
            trails = self.get_trails_for_city(city)
            if not trails:
                return []

            # Filter trails based on weather conditions
            filtered_trails = []
            for trail in trails:
                # Check precipitation
                if max_precipitation is not None and weather["precipitation"] > max_precipitation:
                    continue
                
                # Check temperature
                if min_temperature is not None and weather["temperature_avg"] < min_temperature:
                    continue
                if max_temperature is not None and weather["temperature_avg"] > max_temperature:
                    continue
                
                # Add comfort index to trail data
                trail_with_comfort = trail.copy()
                trail_with_comfort['comfort_index'] = WeatherUtils.calculate_hiking_comfort(weather)
                filtered_trails.append(trail_with_comfort)

            print(f"Znaleziono {len(filtered_trails)} szlaków spełniających kryteria pogodowe")
            return filtered_trails

        except Exception as e:
            print(f"Błąd podczas filtrowania tras według warunków pogodowych: {e}")
            return []

    def get_trails_by_all_criteria(self, city: str, date: str,
                                 difficulty: int = None,
                                 terrain_type: str = None,
                                 max_precipitation: float = None,
                                 min_temperature: float = None,
                                 max_temperature: float = None,
                                 min_length: float = None,
                                 max_length: float = None,
                                 min_sunshine: float = None) -> List[Dict[str, Any]]:
        """Get trails filtered by all criteria."""
        try:
            # Filter trails by city
            city_trails = [trail for trail in self.trails_data if trail.get('region', '').lower() == city.lower()]
            print(f"Znaleziono {len(city_trails)} szlaków dla miasta {city}")

            if not city_trails:
                print(f"Nie znaleziono szlaków dla miasta {city}")
                return []

            # Get weather data
            print(f"Pobieranie danych pogodowych dla {city} na dzień {date}...")
            weather = self.weather_api.get_weather_forecast(city, date)
            if not weather:
                print(f"Brak danych pogodowych dla {city} na dzień {date}")
                return []

            # Filter trails by all criteria
            filtered_trails = []
            for trail in city_trails:
                # Check difficulty
                if difficulty is not None and trail.get('difficulty') != difficulty:
                    continue

                # Check terrain type
                if terrain_type and trail.get('terrain_type', '').lower() != terrain_type.lower():
                    continue

                # Check length
                if min_length is not None and trail.get('length_km', 0) < min_length:
                    continue
                if max_length is not None and trail.get('length_km', 0) > max_length:
                    continue

                # Check weather conditions
                if max_precipitation is not None and weather.get('precipitation', 0) > max_precipitation:
                    continue
                if min_temperature is not None and weather.get('temperature_min', 0) < min_temperature:
                    continue
                if max_temperature is not None and weather.get('temperature_max', 0) > max_temperature:
                    continue
                if min_sunshine is not None and weather.get('sunshine_hours', 0) < min_sunshine:
                    continue

                filtered_trails.append(trail)

            if not filtered_trails:
                print("Nie znaleziono tras spełniających podane kryteria")
                return []

            return filtered_trails

        except Exception as e:
            print(f"Błąd podczas filtrowania tras: {e}")
            return [] 