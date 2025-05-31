import requests
import re
import os
import json
from typing import List, Dict, Any
from functools import reduce
from config import OVERPASS_API, OVERPASS_QUERY_TEMPLATE

class TrailsAPI:
    def __init__(self):
        self.base_url = OVERPASS_API
        self.data_dir = "api"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _parse_distance(self, distance_str: str) -> float:
        """Konwertuje ciąg znaków z odległością na kilometry."""
        if not distance_str:
            return 0.0
        
        try:
            # Usuwa wszystkie znaki niebędące cyframi lub kropkami i konwertuje na float
            value = float(''.join(c for c in str(distance_str) if c.isdigit() or c == '.'))
            
            # Jeśli ciąg zawiera 'm' lub 'km', używa tego jako jednostki
            if isinstance(distance_str, str):
                distance_str = distance_str.lower().strip()
                if 'km' in distance_str:
                    return value
                elif 'm' in distance_str:
                    return value / 1000
                else:
                    # Jeśli nie podano jednostki, zakłada metry jeśli wartość > 100, w przeciwnym razie kilometry
                    return value / 1000 if value > 100 else value
            else:
                # Jeśli nie podano jednostki, zakłada metry jeśli wartość > 100, w przeciwnym razie kilometry
                return value / 1000 if value > 100 else value
                
        except (ValueError, AttributeError):
            return 0.0

    def _parse_elevation(self, elevation_str: str) -> float:
        """Konwertuje ciąg znaków z wysokością na metry."""
        if not elevation_str:
            return 0.0
        
        try:
            # Usuwa wszystkie znaki niebędące cyframi lub kropkami i konwertuje na float
            value = float(''.join(c for c in str(elevation_str) if c.isdigit() or c == '.'))
            
            # Jeśli ciąg zawiera 'm' lub 'km', używa tego jako jednostki
            if isinstance(elevation_str, str):
                elevation_str = elevation_str.lower().strip()
                if 'km' in elevation_str:
                    return value * 1000
                elif 'm' in elevation_str:
                    return value
                else:
                    return value  # Domyślnie zakłada metry
            else:
                return value  # Domyślnie zakłada metry
                
        except (ValueError, AttributeError):
            return 0.0

    def _calculate_difficulty_components(self, tags: Dict[str, str], length_km: float, elevation_m: float) -> List[int]:
        """Oblicza komponenty trudności trasy używając programowania funkcyjnego."""
        components = []
        
        # Komponent długości
        components.append(3 if length_km > 20 else (2 if length_km > 10 else 1))
        
        # Komponent wysokości
        components.append(3 if elevation_m > 1000 else (2 if elevation_m > 500 else 1))
        
        # Komponent skali SAC
        sac_scale = tags.get("sac_scale", "").lower()
        components.append(3 if "alpine" in sac_scale else (2 if "mountain" in sac_scale else 1))
        
        # Komponent powierzchni
        surface = tags.get("surface", "").lower()
        components.append(3 if any(s in surface for s in ["rock", "scree"]) else 
                         (2 if any(s in surface for s in ["gravel", "dirt"]) else 1))
        
        # Komponent nachylenia
        incline = float(tags.get("incline", "0").replace("%", "")) if tags.get("incline") else 0
        components.append(3 if incline > 15 else (2 if incline > 10 else 1))
        
        return components

    def _calculate_difficulty(self, tags: Dict[str, str], length_km: float, elevation_m: float) -> int:
        """Oblicza trudność trasy używając funkcji reduce."""
        components = self._calculate_difficulty_components(tags, length_km, elevation_m)
        # Używa reduce aby znaleźć maksymalny komponent trudności
        max_difficulty = reduce(lambda x, y: max(x, y), components)
        return max(1, min(3, max_difficulty))

    def get_hiking_trails(self, city: str) -> List[Dict[str, Any]]:
        """Pobiera szlaki turystyczne dla miasta używając API Overpass."""
        print(f"\nPróba pobrania tras dla miasta: {city}")

        # Expanded Overpass query to find more trails
        query = f"""
        [out:json][timeout:25];
        area["name"="{city}"]["boundary"="administrative"]->.searchArea;
        (
          // Main hiking and walking routes
          relation["route"~"hiking|foot|walking|running"](area.searchArea);
          way["route"~"hiking|foot|walking|running"](area.searchArea);
          
          // Parks and nature reserves
          relation["leisure"~"park|nature_reserve|garden"](area.searchArea);
          way["leisure"~"park|nature_reserve|garden"](area.searchArea);
          
          // Natural areas
          relation["natural"~"wood|forest|park|heath|grassland|scrub"](area.searchArea);
          way["natural"~"wood|forest|park|heath|grassland|scrub"](area.searchArea);
          
          // Tourist attractions
          relation["tourism"~"attraction|viewpoint|picnic_site"](area.searchArea);
          way["tourism"~"attraction|viewpoint|picnic_site"](area.searchArea);
          
          // Waterways and coastlines
          relation["waterway"~"river|stream|canal"](area.searchArea);
          way["waterway"~"river|stream|canal"](area.searchArea);
          relation["natural"~"coastline|beach"](area.searchArea);
          way["natural"~"coastline|beach"](area.searchArea);
          
          // Historical and cultural sites
          relation["historic"~"monument|memorial|castle|ruins"](area.searchArea);
          way["historic"~"monument|memorial|castle|ruins"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """

        try:
            print(f"Wysyłanie zapytania do API Overpass dla {city}")
            response = requests.post(self.base_url, data={"data": query})
            response.raise_for_status()
            data = response.json()
            print(f"Otrzymano odpowiedź z API dla {city}")

            # Use map to process all elements
            trails = list(map(lambda element: self._process_trail_element(element, city), 
                            filter(lambda e: e.get("type") in ["relation", "way"], 
                                  data.get("elements", []))))

            # Filter out None values and empty trails
            trails = list(filter(None, trails))
            
            print(f"Znaleziono łącznie {len(trails)} tras dla {city}")
            
            # Save trails to file
            file_path = os.path.join(self.data_dir, "trails_data.json")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(trails, f, ensure_ascii=False, indent=2)
                print(f"Zapisano dane o szlakach do pliku {file_path}")
            except Exception as e:
                print(f"Błąd podczas zapisywania danych o szlakach: {e}")
            
            return trails

        except requests.RequestException as e:
            print(f"Błąd podczas pobierania danych dla {city}: {e}")
            return []

    def _process_trail_element(self, element: Dict[str, Any], city: str) -> Dict[str, Any]:
        """Przetwarza pojedynczy element szlaku."""
        tags = element.get("tags", {})
        
        # Skip if no name
        if not tags.get("name"):
            return None
            
        # Calculate length from various possible sources
        length_sources = [
            tags.get("distance"),
            tags.get("length"),
            tags.get("way_length"),
            tags.get("route_length")
        ]
        
        length_km = 0.0
        for source in length_sources:
            if source:
                length_km = self._parse_distance(source)
                if length_km > 0:
                    break
        
        # Skip trails with unknown length
        if length_km == 0:
            return None

        # Get elevation data
        elevation_sources = [
            tags.get("ele"),
            tags.get("elevation"),
            tags.get("height")
        ]
        
        elevation_m = 0.0
        for source in elevation_sources:
            if source:
                elevation_m = self._parse_elevation(source)
                if elevation_m > 0:
                    break

        # Get coordinates if available
        coordinates = None
        try:
            if "center" in element and isinstance(element["center"], dict):
                coordinates = {
                    "lat": element["center"].get("lat"),
                    "lon": element["center"].get("lon")
                }
            elif "nodes" in element and element["nodes"] and isinstance(element["nodes"], list):
                # Use first node as approximate location
                first_node = element["nodes"][0]
                if isinstance(first_node, dict):
                    coordinates = {
                        "lat": first_node.get("lat"),
                        "lon": first_node.get("lon")
                    }
        except (KeyError, IndexError, TypeError) as e:
            print(f"Błąd podczas pobierania współrzędnych: {e}")
            coordinates = None
        
        trail = {
            "id": str(element.get("id")),
            "name": tags.get("name", "Unknown Trail"),
            "region": city,
            "coordinates": coordinates,
            "length_km": length_km,
            "elevation_m": elevation_m,
            "difficulty": self._calculate_difficulty(tags, length_km, elevation_m),
            "terrain_type": self._determine_terrain_type(tags),
            "tags": [k for k, v in tags.items() if v == "yes"]
        }
        
        print(f"Znaleziono trasę: {trail['name']} ({trail['length_km']:.2f} km, trudność: {trail['difficulty']})")
        return trail

    def _determine_terrain_type(self, tags: Dict[str, str]) -> str:
        """Określa typ terenu używając list składanych."""
        terrain_mapping = {
            "waterway": "riverside",
            "natural=coast": "coastal",
            "leisure=park": "park",
            "historic": "historical",
            "place=city": "urban",
            "place=town": "urban"
        }
        
        # Use dictionary comprehension to find matching terrain type
        terrain_type = next((v for k, v in terrain_mapping.items() 
                           if k in tags or any(k in str(v).lower() for v in tags.values())), 
                          "mixed")
        return terrain_type 