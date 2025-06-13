from enum import Enum
import os

class TerrainType(Enum):
    GRASS = "grass"
    WATER = "water"
    MOUNTAIN = "mountain"
    SAND = "sand"
    ROAD = "road"
    SIDEWALK = "sidewalk"

class BuildingType(Enum):
    # Infrastructure
    ROAD = "road"
    ROAD_CURVE = "road_curve"
    SIDEWALK = "sidewalk"
    
    # Residential
    HOUSE = "house"
    RESIDENTIAL = "residential"
    APARTMENT = "apartment"
    
    # Commercial
    COMMERCIAL = "commercial"
    SHOP = "shop"
    MALL = "mall"
    
    # Industrial
    INDUSTRIAL = "industrial"
    FACTORY = "factory"
    WAREHOUSE = "warehouse"
    
    # Public Services
    CITY_HALL = "city_hall"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    UNIVERSITY = "university"
    POLICE = "police"
    FIRE_STATION = "fire_station"
    
    # Utilities
    POWER_PLANT = "power_plant"
    WATER_TREATMENT = "water_treatment"
    
    # Recreation
    PARK = "park"
    STADIUM = "stadium"

class Building:
    def __init__(self, name: str, building_type: BuildingType, cost: int, effects: dict, unlock_condition: dict = None):
        self.name = name
        self.building_type = building_type
        self.cost = cost
        self.effects = effects
        self.rotation = 0  # 0, 90, 180, 270 degrees
        self.unlock_condition = unlock_condition or {}  # Np. {'population': 200, 'satisfaction': 60}

    def get_image_path(self) -> str | None:
        """Returns path to the building image or None if using color"""
        base_path = os.path.join("assets", "tiles")
        images = {
            BuildingType.ROAD: "prostadroga.png",
            BuildingType.ROAD_CURVE: "drogazakręt.png", 
            BuildingType.SIDEWALK: "chodnik.png",
            BuildingType.HOUSE: "domek1.png",
            BuildingType.CITY_HALL: "burmistrzbudynek.png"
        }
        if self.building_type in images:
            return os.path.join(base_path, images[self.building_type])
        return None

    def get_color(self) -> str:
        """Returns color for the building type if no image is available"""
        colors = {
            # Infrastructure
            BuildingType.ROAD: "#808080",         # Gray
            BuildingType.ROAD_CURVE: "#808080",   # Gray
            BuildingType.SIDEWALK: "#DEB887",     # Burly Wood
            
            # Residential
            BuildingType.HOUSE: "#90EE90",        # Light Green
            BuildingType.RESIDENTIAL: "#FFB6C1",  # Light Pink
            BuildingType.APARTMENT: "#FFA0B4",    # Darker Pink
            
            # Commercial
            BuildingType.COMMERCIAL: "#FFD700",   # Gold
            BuildingType.SHOP: "#FFA500",         # Orange
            BuildingType.MALL: "#FFD700",         # Gold
            
            # Industrial
            BuildingType.INDUSTRIAL: "#8B4513",   # Brown
            BuildingType.FACTORY: "#A0522D",      # Sienna
            BuildingType.WAREHOUSE: "#D2691E",    # Chocolate
            
            # Public Services
            BuildingType.CITY_HALL: "#4169E1",    # Royal Blue
            BuildingType.HOSPITAL: "#FF6347",     # Tomato
            BuildingType.SCHOOL: "#32CD32",       # Lime Green
            BuildingType.UNIVERSITY: "#228B22",   # Forest Green
            BuildingType.POLICE: "#0000FF",       # Blue
            BuildingType.FIRE_STATION: "#DC143C", # Crimson
            
            # Utilities
            BuildingType.POWER_PLANT: "#FFFF00",  # Yellow
            BuildingType.WATER_TREATMENT: "#00CED1", # Dark Turquoise
            
            # Recreation
            BuildingType.PARK: "#7CFC00",         # Lawn Green
            BuildingType.STADIUM: "#9370DB",      # Medium Purple
        }
        return colors.get(self.building_type, "#808080")  # Default gray

    def rotate(self):
        """Rotates the building 90 degrees clockwise"""
        self.rotation = (self.rotation + 90) % 360

class Tile:
    def __init__(self, x: int, y: int, terrain_type: TerrainType = TerrainType.GRASS):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.building = None
        self.is_occupied = False
        
    def get_image_path(self) -> str | None:
        """Returns path to the tile image or None if using color"""
        base_path = os.path.join("assets", "tiles")
        images = {
            TerrainType.GRASS: "grassnew.png",
            TerrainType.SIDEWALK: "chodnik.png"
        }
        if self.terrain_type in images:
            return os.path.join(base_path, images[self.terrain_type])
        return None
    
    def get_color(self) -> str:
        """Returns color for the terrain type"""
        colors = {
            TerrainType.GRASS: "#90EE90",    # Light green
            TerrainType.WATER: "#4169E1",    # Royal blue
            TerrainType.MOUNTAIN: "#4A4A4A", # Dark gray
            TerrainType.SAND: "#F4A460",     # Sandy brown
            TerrainType.ROAD: "#808080",     # Gray
            TerrainType.SIDEWALK: "#DEB887"  # Burly Wood
        }
        return colors.get(self.terrain_type, "#FFFFFF")  # Default white
    
    def __str__(self) -> str:
        return f"Tile({self.x}, {self.y}) - {self.terrain_type.value}" 