"""
Configuration settings for the trail recommendation system.
"""
from typing import Dict

# API Endpoints
OPEN_METEO_API = "https://api.open-meteo.com/v1"
OVERPASS_API = "https://overpass-api.de/api/interpreter"

# City coordinates for weather data
CITY_COORDINATES: Dict[str, Dict[str, float]] = {
    "Gdańsk": {"lat": 54.3520, "lon": 18.6466},
    "Warszawa": {"lat": 52.2297, "lon": 21.0122},
    "Kraków": {"lat": 50.0647, "lon": 19.9450},
    "Wrocław": {"lat": 51.1079, "lon": 17.0385}
}

# Overpass API query template
OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:25];
area["name"="{city}"]["boundary"="administrative"]->.searchArea;
relation["type"="route"]["route"="hiking"](area.searchArea);
out body;
>;
out skel qt;
""" 