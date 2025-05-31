"""
API package for trail and weather data retrieval.
"""

from .trails_api import TrailsAPI
from .weather_api import WeatherAPI

__all__ = ['TrailsAPI', 'WeatherAPI'] 