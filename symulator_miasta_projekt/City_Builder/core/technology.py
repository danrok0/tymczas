"""
Rozszerzony system technologii dla City Builder
Implementuje drzewko technologiczne z 25+ technologiami i zależnościami
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

class TechnologyCategory(Enum):
    INFRASTRUCTURE = "infrastructure"
    ECONOMY = "economy"
    SOCIAL = "social"
    ENVIRONMENT = "environment"
    MILITARY = "military"
    SCIENCE = "science"

@dataclass
class Technology:
    """Reprezentuje pojedynczą technologię"""
    id: str
    name: str
    description: str
    category: TechnologyCategory
    cost: int
    research_time: int  # Liczba tur potrzebnych do badania
    prerequisites: List[str]  # Lista ID technologii wymaganych
    effects: Dict[str, float]  # Efekty technologii
    unlocks_buildings: List[str] = None  # Budynki odblokowane przez technologię
    unlocks_technologies: List[str] = None  # Technologie odblokowane przez tę
    is_researched: bool = False
    research_progress: int = 0
    
    def __post_init__(self):
        if self.unlocks_buildings is None:
            self.unlocks_buildings = []
        if self.unlocks_technologies is None:
            self.unlocks_technologies = []

class TechnologyManager:
    """Zarządza systemem technologii"""
    
    def __init__(self):
        self.technologies = {}
        self.research_queue = []
        self.current_research = None
        self.research_points_per_turn = 1
        self.total_research_investment = 0
        
        self._initialize_technologies()
    
    def _initialize_technologies(self):
        """Inicjalizuje wszystkie dostępne technologie"""
        
        # TIER 1 - Podstawowe technologie
        technologies_data = [
            # INFRASTRUKTURA
            {
                "id": "basic_construction",
                "name": "Podstawowe Budownictwo",
                "description": "Ulepszone techniki budowlane zwiększają efektywność budowy",
                "category": TechnologyCategory.INFRASTRUCTURE,
                "cost": 500,
                "research_time": 3,
                "prerequisites": [],
                "effects": {"construction_cost_reduction": 0.1, "building_efficiency": 0.05},
                "unlocks_buildings": ["improved_house"]
            },
            {
                "id": "road_engineering",
                "name": "Inżynieria Drogowa",
                "description": "Zaawansowane techniki budowy dróg i mostów",
                "category": TechnologyCategory.INFRASTRUCTURE,
                "cost": 800,
                "research_time": 4,
                "prerequisites": ["basic_construction"],
                "effects": {"traffic_efficiency": 0.2, "transport_cost_reduction": 0.15},
                "unlocks_buildings": ["highway", "bridge"]
            },
            {
                "id": "urban_planning",
                "name": "Planowanie Urbanistyczne",
                "description": "Efektywne planowanie przestrzenne miasta",
                "category": TechnologyCategory.INFRASTRUCTURE,
                "cost": 1200,
                "research_time": 5,
                "prerequisites": ["road_engineering"],
                "effects": {"city_efficiency": 0.1, "happiness_bonus": 0.05},
                "unlocks_buildings": ["city_center", "plaza"]
            },
            
            # EKONOMIA
            {
                "id": "basic_economics",
                "name": "Podstawy Ekonomii",
                "description": "Lepsze zrozumienie mechanizmów ekonomicznych",
                "category": TechnologyCategory.ECONOMY,
                "cost": 600,
                "research_time": 3,
                "prerequisites": [],
                "effects": {"tax_efficiency": 0.1, "trade_bonus": 0.05},
                "unlocks_buildings": ["bank"]
            },
            {
                "id": "banking",
                "name": "Bankowość",
                "description": "System bankowy zwiększa przepływ kapitału",
                "category": TechnologyCategory.ECONOMY,
                "cost": 1000,
                "research_time": 4,
                "prerequisites": ["basic_economics"],
                "effects": {"interest_rate_reduction": 0.2, "loan_capacity": 0.3},
                "unlocks_buildings": ["central_bank", "stock_exchange"]
            },
            {
                "id": "industrialization",
                "name": "Industrializacja",
                "description": "Rozwój przemysłu zwiększa produkcję",
                "category": TechnologyCategory.ECONOMY,
                "cost": 1500,
                "research_time": 6,
                "prerequisites": ["banking", "basic_construction"],
                "effects": {"industrial_efficiency": 0.25, "job_creation": 0.2},
                "unlocks_buildings": ["steel_mill", "chemical_plant"]
            },
            
            # SPOŁECZNE
            {
                "id": "public_education",
                "name": "Edukacja Publiczna",
                "description": "System edukacji publicznej dla wszystkich",
                "category": TechnologyCategory.SOCIAL,
                "cost": 800,
                "research_time": 4,
                "prerequisites": [],
                "effects": {"education_efficiency": 0.2, "research_speed": 0.1},
                "unlocks_buildings": ["public_school", "library"]
            },
            {
                "id": "healthcare_system",
                "name": "System Opieki Zdrowotnej",
                "description": "Zorganizowana opieka medyczna",
                "category": TechnologyCategory.SOCIAL,
                "cost": 1000,
                "research_time": 5,
                "prerequisites": ["public_education"],
                "effects": {"health_efficiency": 0.25, "population_growth": 0.1},
                "unlocks_buildings": ["clinic", "pharmacy"]
            },
            {
                "id": "social_services",
                "name": "Usługi Społeczne",
                "description": "Kompleksowe wsparcie społeczne",
                "category": TechnologyCategory.SOCIAL,
                "cost": 1200,
                "research_time": 5,
                "prerequisites": ["healthcare_system"],
                "effects": {"happiness_bonus": 0.15, "crime_reduction": 0.1},
                "unlocks_buildings": ["social_center", "elderly_home"]
            },
            
            # ŚRODOWISKO
            {
                "id": "environmental_awareness",
                "name": "Świadomość Ekologiczna",
                "description": "Podstawowa wiedza o ochronie środowiska",
                "category": TechnologyCategory.ENVIRONMENT,
                "cost": 700,
                "research_time": 3,
                "prerequisites": [],
                "effects": {"pollution_reduction": 0.1, "green_bonus": 0.05},
                "unlocks_buildings": ["recycling_center"]
            },
            {
                "id": "renewable_energy",
                "name": "Energia Odnawialna",
                "description": "Czyste źródła energii",
                "category": TechnologyCategory.ENVIRONMENT,
                "cost": 1500,
                "research_time": 6,
                "prerequisites": ["environmental_awareness", "basic_construction"],
                "effects": {"energy_efficiency": 0.3, "pollution_reduction": 0.2},
                "unlocks_buildings": ["solar_plant", "wind_farm"]
            },
            {
                "id": "green_technology",
                "name": "Zielone Technologie",
                "description": "Zaawansowane technologie ekologiczne",
                "category": TechnologyCategory.ENVIRONMENT,
                "cost": 2000,
                "research_time": 8,
                "prerequisites": ["renewable_energy"],
                "effects": {"eco_efficiency": 0.25, "sustainability_bonus": 0.2},
                "unlocks_buildings": ["eco_district", "green_skyscraper"]
            },
            
            # NAUKA
            {
                "id": "scientific_method",
                "name": "Metoda Naukowa",
                "description": "Systematyczne podejście do badań",
                "category": TechnologyCategory.SCIENCE,
                "cost": 1000,
                "research_time": 4,
                "prerequisites": ["public_education"],
                "effects": {"research_speed": 0.2, "technology_cost_reduction": 0.1},
                "unlocks_buildings": ["research_lab"]
            },
            {
                "id": "advanced_materials",
                "name": "Zaawansowane Materiały",
                "description": "Nowe materiały budowlane i przemysłowe",
                "category": TechnologyCategory.SCIENCE,
                "cost": 1800,
                "research_time": 7,
                "prerequisites": ["scientific_method", "industrialization"],
                "effects": {"construction_efficiency": 0.2, "durability_bonus": 0.15},
                "unlocks_buildings": ["high_tech_factory", "space_center"]
            },
            {
                "id": "information_technology",
                "name": "Technologie Informacyjne",
                "description": "Komputery i systemy informatyczne",
                "category": TechnologyCategory.SCIENCE,
                "cost": 2200,
                "research_time": 8,
                "prerequisites": ["advanced_materials"],
                "effects": {"efficiency_bonus": 0.15, "automation": 0.1},
                "unlocks_buildings": ["tech_park", "data_center"]
            },
            
            # BEZPIECZEŃSTWO
            {
                "id": "law_enforcement",
                "name": "Egzekwowanie Prawa",
                "description": "Profesjonalne służby porządkowe",
                "category": TechnologyCategory.MILITARY,
                "cost": 900,
                "research_time": 4,
                "prerequisites": [],
                "effects": {"crime_reduction": 0.2, "safety_bonus": 0.15},
                "unlocks_buildings": ["police_station", "courthouse"]
            },
            {
                "id": "emergency_services",
                "name": "Służby Ratunkowe",
                "description": "Zorganizowane służby ratownicze",
                "category": TechnologyCategory.MILITARY,
                "cost": 1100,
                "research_time": 5,
                "prerequisites": ["law_enforcement"],
                "effects": {"disaster_resistance": 0.2, "emergency_response": 0.25},
                "unlocks_buildings": ["emergency_center", "disaster_shelter"]
            },
            {
                "id": "civil_defense",
                "name": "Obrona Cywilna",
                "description": "Kompleksowy system obrony miasta",
                "category": TechnologyCategory.MILITARY,
                "cost": 1600,
                "research_time": 6,
                "prerequisites": ["emergency_services"],
                "effects": {"city_defense": 0.3, "crisis_management": 0.2},
                "unlocks_buildings": ["command_center", "bunker"]
            },
            
            # TIER 2 - Zaawansowane technologie
            {
                "id": "smart_city",
                "name": "Inteligentne Miasto",
                "description": "Zintegrowane systemy zarządzania miastem",
                "category": TechnologyCategory.SCIENCE,
                "cost": 3000,
                "research_time": 10,
                "prerequisites": ["information_technology", "urban_planning"],
                "effects": {"city_efficiency": 0.25, "automation": 0.2},
                "unlocks_buildings": ["smart_grid", "automated_transport"]
            },
            {
                "id": "biotechnology",
                "name": "Biotechnologia",
                "description": "Zaawansowane technologie biologiczne",
                "category": TechnologyCategory.SCIENCE,
                "cost": 2800,
                "research_time": 9,
                "prerequisites": ["advanced_materials", "healthcare_system"],
                "effects": {"health_efficiency": 0.3, "food_production": 0.2},
                "unlocks_buildings": ["biotech_lab", "vertical_farm"]
            },
            {
                "id": "fusion_power",
                "name": "Energia Fuzji",
                "description": "Czysta i nieograniczona energia",
                "category": TechnologyCategory.ENVIRONMENT,
                "cost": 4000,
                "research_time": 12,
                "prerequisites": ["green_technology", "advanced_materials"],
                "effects": {"energy_efficiency": 0.5, "pollution_reduction": 0.4},
                "unlocks_buildings": ["fusion_reactor"]
            },
            {
                "id": "space_technology",
                "name": "Technologie Kosmiczne",
                "description": "Eksploracja i wykorzystanie kosmosu",
                "category": TechnologyCategory.SCIENCE,
                "cost": 5000,
                "research_time": 15,
                "prerequisites": ["fusion_power", "smart_city"],
                "effects": {"prestige_bonus": 0.3, "research_speed": 0.3},
                "unlocks_buildings": ["space_elevator", "orbital_station"]
            }
        ]
        
        # Tworzenie obiektów technologii
        for tech_data in technologies_data:
            tech = Technology(**tech_data)
            self.technologies[tech.id] = tech
    
    def can_research(self, tech_id: str) -> tuple[bool, str]:
        """Sprawdza czy można rozpocząć badanie technologii"""
        if tech_id not in self.technologies:
            return False, "Nieznana technologia"
        
        tech = self.technologies[tech_id]
        
        if tech.is_researched:
            return False, "Technologia już zbadana"
        
        if self.current_research:
            return False, "Inne badania w toku"
        
        # Sprawdź prerequisity
        for prereq in tech.prerequisites:
            if not self.technologies[prereq].is_researched:
                return False, f"Wymagana technologia: {self.technologies[prereq].name}"
        
        return True, "OK"
    
    def start_research(self, tech_id: str, investment: int = 0) -> bool:
        """Rozpoczyna badanie technologii"""
        can_research, reason = self.can_research(tech_id)
        if not can_research:
            return False
        
        self.current_research = tech_id
        self.total_research_investment += investment
        
        # Inwestycja zwiększa szybkość badań
        if investment > 0:
            bonus_points = investment // 1000  # 1 punkt za każde 1000$
            self.research_points_per_turn = 1 + bonus_points
        
        return True
    
    def update_research(self) -> Optional[Technology]:
        """Aktualizuje postęp badań, zwraca ukończoną technologię"""
        if not self.current_research:
            return None
        
        tech = self.technologies[self.current_research]
        tech.research_progress += self.research_points_per_turn
        
        if tech.research_progress >= tech.research_time:
            # Technologia ukończona
            tech.is_researched = True
            completed_tech = tech
            self.current_research = None
            self.research_points_per_turn = 1
            
            return completed_tech
        
        return None
    
    def get_available_technologies(self) -> List[Technology]:
        """Zwraca technologie dostępne do badania"""
        available = []
        for tech in self.technologies.values():
            if not tech.is_researched:
                can_research, _ = self.can_research(tech.id)
                if can_research or not self.current_research:
                    available.append(tech)
        return available
    
    def get_researched_technologies(self) -> List[Technology]:
        """Zwraca zbadane technologie"""
        return [tech for tech in self.technologies.values() if tech.is_researched]
    
    def get_technology_effects(self) -> Dict[str, float]:
        """Zwraca skumulowane efekty wszystkich zbadanych technologii"""
        effects = {}
        for tech in self.get_researched_technologies():
            for effect, value in tech.effects.items():
                effects[effect] = effects.get(effect, 0) + value
        return effects
    
    def get_unlocked_buildings(self) -> List[str]:
        """Zwraca budynki odblokowane przez technologie"""
        buildings = []
        for tech in self.get_researched_technologies():
            buildings.extend(tech.unlocks_buildings)
        return buildings
    
    def save_to_dict(self) -> Dict:
        """Zapisuje stan do słownika"""
        return {
            'current_research': self.current_research,
            'research_points_per_turn': self.research_points_per_turn,
            'total_research_investment': self.total_research_investment,
            'technologies': {
                tech_id: {
                    'is_researched': tech.is_researched,
                    'research_progress': tech.research_progress
                }
                for tech_id, tech in self.technologies.items()
            }
        }
    
    def load_from_dict(self, data: Dict):
        """Wczytuje stan ze słownika"""
        self.current_research = data.get('current_research')
        self.research_points_per_turn = data.get('research_points_per_turn', 1)
        self.total_research_investment = data.get('total_research_investment', 0)
        
        tech_data = data.get('technologies', {})
        for tech_id, tech_state in tech_data.items():
            if tech_id in self.technologies:
                self.technologies[tech_id].is_researched = tech_state.get('is_researched', False)
                self.technologies[tech_id].research_progress = tech_state.get('research_progress', 0) 