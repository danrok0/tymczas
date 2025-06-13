from typing import List, Dict, Optional
from .city_map import CityMap
from .resources import Economy
from .population import PopulationManager
from .tile import Building, BuildingType, TerrainType
from .technology import TechnologyManager
from .trade import TradeManager
from .achievements import AchievementManager
import time
from copy import deepcopy

class GameEngine:
    """Main game engine that coordinates all city systems"""
    
    def __init__(self, map_width: int = 60, map_height: int = 60):
        # Core systems
        self.city_map = CityMap(map_width, map_height)
        self.economy = Economy()
        self.population = PopulationManager()
        
        # New advanced systems
        self.technology_manager = TechnologyManager()
        self.trade_manager = TradeManager()
        self.achievement_manager = AchievementManager()
        
        # Game state
        self.turn = 0
        self.game_speed = 1.0  # Speed multiplier
        self.paused = False
        self.last_update = time.time()
        
        # City level system
        self.city_level = 1
        self.level_requirements = {
            1: 0,      # Start at level 1
            2: 600,    # Level 2: 600
            3: 1400,   # Level 3: 1400
            4: 2800,   # Level 4: 2800
            5: 5000,   # Level 5: 5000
            6: 8000,   # Level 6: 8000
            7: 12000,  # Level 7: 12000
            8: 17000,  # Level 8: 17000
            9: 23000,  # Level 9: 23000
            10: 30000  # Level 10: 30000
        }
        
        # Difficulty settings
        self.difficulty = "Normal"
        self.difficulty_modifiers = {
            "Easy": {"cost_multiplier": 0.8, "income_multiplier": 1.2, "event_frequency": 0.5},
            "Normal": {"cost_multiplier": 1.0, "income_multiplier": 1.0, "event_frequency": 1.0},
            "Hard": {"cost_multiplier": 1.3, "income_multiplier": 0.8, "event_frequency": 1.5}
        }
        
        # Enhanced statistics tracking
        self.statistics = {
            'buildings_built': 0,
            'total_money_spent': 0,
            'max_population': 0,
            'turns_played': 0,
            'technologies_researched': 0,
            'trades_completed': 0,
            'total_tax_collected': 0,
            'unemployment_streak': 0,
            'building_types_built': set(),
            'parks_built': 0,
            'pollution_level': 0,
            'renewable_energy_percent': 0,
            'disasters_survived': 0,
            'crisis_events_resolved': 0,
            'perfect_happiness_streak': 0,
            'allied_cities': 0
        }
        
        # Alerts system
        self.alerts = []
        
    def get_all_buildings(self) -> List[Building]:
        """Get all buildings from the map"""
        buildings = []
        for x in range(self.city_map.width):
            for y in range(self.city_map.height):
                tile = self.city_map.get_tile(x, y)
                if tile and tile.building:
                    buildings.append(tile.building)
        return buildings
    
    def can_build(self, x: int, y: int, building: Building) -> tuple[bool, str]:
        """Check if a building can be placed, returns (can_build, reason)"""
        # Check tile availability
        tile = self.city_map.get_tile(x, y)
        if not tile:
            return False, "Invalid location"
        
        if tile.is_occupied:
            return False, "Tile already occupied"
        
        # Check resources
        cost = self.get_adjusted_cost(building.cost)
        if not self.economy.can_afford(cost):
            return False, f"Insufficient funds. Need ${cost:,.0f}, have ${self.economy.get_resource_amount('money'):,.0f}"
        
        # Check terrain compatibility - block building on water and mountains
        if tile.terrain_type.value == 'water':
            return False, "Cannot build on water"
        if tile.terrain_type.value == 'mountain':
            return False, "Cannot build on mountains"
        
        return True, "OK"
    
    def place_building(self, x: int, y: int, building: Building) -> bool:
        """Place a building on the map"""
        can_build, reason = self.can_build(x, y, building)
        if not can_build:
            self.add_alert(f"Cannot build: {reason}")
            return False
        
        # Place building - use the building directly (already copied in MapCanvas)
        tile = self.city_map.get_tile(x, y)
        
        tile.building = building  # Nie robimy deepcopy - budynek już jest skopiowany z rotacją
        tile.is_occupied = True
        
        # If residential, instantly add population
        if hasattr(building, 'effects') and 'population' in building.effects:
            self.population.add_instant_population(building.effects['population'])
        
        # Deduct cost
        cost = self.get_adjusted_cost(building.cost)
        self.economy.spend_money(cost)
        
        # Update statistics
        self.statistics['buildings_built'] += 1
        self.statistics['total_money_spent'] += cost
        self.statistics['building_types_built'].add(building.building_type.value)
        
        # Track specific building types
        if building.building_type == BuildingType.PARK:
            self.statistics['parks_built'] += 1
        
        self.add_alert(f"Built {building.name} for ${cost:,.0f}")
        return True
    
    def remove_building(self, x: int, y: int) -> bool:
        """Remove a building from the map and refund half its cost. Also remove its effects from city systems and update all stats."""
        tile = self.city_map.get_tile(x, y)
        if not tile or not tile.building:
            return False
        building = tile.building
        building_name = building.name
        building_cost = building.cost
        # Usuwanie efektów budynku
        if hasattr(building, 'effects'):
            effects = building.effects
            # Populacja
            if 'population' in effects:
                self.population.add_instant_population(-effects['population'])
            # Praca
            if 'jobs' in effects:
                pass
        tile.building = None
        tile.is_occupied = False
        # Refund half the cost
        refund = building_cost * 0.5
        self.economy.earn_money(refund)
        # Wymuś pełną aktualizację wszystkich systemów/statystyk
        buildings = self.get_all_buildings()
        self.population.calculate_needs(buildings)
        self.population.update_population_dynamics()
        self.update_city_level()
        # Statystyki ekonomiczne i inne są aktualizowane w update_turn, ale tu wymuszamy przeliczenie
        self.economy.update_turn(buildings, self.population)
        self.add_alert(f"Sprzedano {building_name} za ${refund:,.0f}")
        return True
    
    def get_adjusted_cost(self, base_cost: float) -> float:
        """Get cost adjusted for difficulty"""
        modifier = self.difficulty_modifiers[self.difficulty]["cost_multiplier"]
        return base_cost * modifier
    
    def update_turn(self):
        """Update all systems for one game turn"""
        if self.paused:
            return
        
        # Get all buildings
        buildings = self.get_all_buildings()
        
        # Update population needs and dynamics
        self.population.calculate_needs(buildings)
        self.population.update_population_dynamics()
        self.update_city_level()  # Update city level
        
        # Update economy (pass population_manager)
        self.economy.update_turn(buildings, self.population)
        
        # Update advanced systems
        self.technology_manager.update_research()
        self.trade_manager.current_turn = self.turn
        self.trade_manager.update_turn()
        
        # Update enhanced statistics
        self._update_enhanced_statistics(buildings)
        
        # Check achievements
        newly_unlocked = self.achievement_manager.check_achievements(self.statistics)
        for achievement in newly_unlocked:
            self.add_alert(f"🏆 Osiągnięcie odblokowane: {achievement.name}!", priority="achievement")
        
        # Check for critical situations
        self._check_critical_situations()
        
        self.turn += 1
        self.statistics['turns_played'] = self.turn
    
    def _update_enhanced_statistics(self, buildings: List[Building]):
        """Update enhanced statistics for achievements"""
        # Basic population stats
        current_pop = self.population.get_total_population()
        if current_pop > self.statistics['max_population']:
            self.statistics['max_population'] = current_pop
        
        # Current population for achievements
        self.statistics['population'] = current_pop
        self.statistics['money'] = self.economy.get_resource_amount('money')
        
        # Technology stats
        self.statistics['technologies_researched'] = len(self.technology_manager.get_researched_technologies())
        
        # Trade stats
        trade_stats = self.trade_manager.get_trade_statistics()
        self.statistics['trades_completed'] = trade_stats['total_trades']
        
        # Count allied cities
        allied_count = 0
        for city_name, city_data in trade_stats['relationships'].items():
            if city_data['status'] == 'allied':
                allied_count += 1
        self.statistics['allied_cities'] = allied_count
        
        # Unemployment tracking for achievements
        unemployment_rate = self.population.get_unemployment_rate()
        if unemployment_rate == 0:
            self.statistics['unemployment_streak'] += 1
        else:
            self.statistics['unemployment_streak'] = 0
        
        # Happiness tracking
        satisfaction = self.population.get_average_satisfaction()
        if satisfaction >= 100:
            self.statistics['perfect_happiness_streak'] += 1
        else:
            self.statistics['perfect_happiness_streak'] = 0
        
        # Tax collection tracking
        # This would need to be tracked in economy system
        
        # Environmental stats (placeholder - would need actual implementation)
        self.statistics['pollution_level'] = max(0, 50 - len([b for b in buildings if b.building_type == BuildingType.PARK]))
        
        # Count renewable energy buildings
        renewable_buildings = [b for b in buildings if 'renewable' in b.name.lower() or 'solar' in b.name.lower() or 'wind' in b.name.lower()]
        total_energy_buildings = [b for b in buildings if 'power' in b.name.lower() or 'energy' in b.name.lower()]
        if total_energy_buildings:
            self.statistics['renewable_energy_percent'] = (len(renewable_buildings) / len(total_energy_buildings)) * 100
        else:
            self.statistics['renewable_energy_percent'] = 0
    
    def _check_critical_situations(self):
        """Check for situations that require player attention"""
        # Low money warning
        if self.economy.get_resource_amount('money') < 5000:
            self.add_alert("⚠️ Treasury running low!", priority="warning")
        
        # Low satisfaction warning
        avg_satisfaction = self.population.get_average_satisfaction()
        if avg_satisfaction < 30:
            self.add_alert("😞 Population satisfaction is very low!", priority="warning")
        
        # High unemployment warning
        unemployment = self.population.get_unemployment_rate()
        if unemployment > 20:
            self.add_alert(f"📈 High unemployment: {unemployment:.1f}%", priority="warning")
        
        # Resource shortages
        for need_name, need_data in self.population.needs.items():
            if need_data['satisfaction'] < 25:
                self.add_alert(f"🏥 Shortage of {need_name}", priority="info")
    
    def add_alert(self, message: str, priority: str = "info"):
        """Add an alert message"""
        alert = {
            'message': message,
            'priority': priority,
            'turn': self.turn,
            'timestamp': time.time()
        }
        self.alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts.pop(0)
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """Get recent alerts"""
        return self.alerts[-count:]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
    
    def set_difficulty(self, difficulty: str):
        """Set game difficulty"""
        if difficulty in self.difficulty_modifiers:
            self.difficulty = difficulty
            self.add_alert(f"Difficulty set to {difficulty}")
        
    def pause_game(self):
        """Pause the game"""
        self.paused = True
        
    def resume_game(self):
        """Resume the game"""
        self.paused = False
        
    def set_game_speed(self, speed: float):
        """Set game speed multiplier"""
        self.game_speed = max(0.1, min(5.0, speed))  # Clamp between 0.1x and 5x
    
    def get_city_summary(self) -> Dict:
        """Get a comprehensive summary of city status"""
        buildings = self.get_all_buildings()
        demographics = self.population.get_demographics()
        resources = self.economy.get_resource_summary()
        
        return {
            'turn': self.turn,
            'difficulty': self.difficulty,
            'paused': self.paused,
            'city_name': f"City Turn {self.turn}",  # Could be customizable
            
            # Economy
            'money': resources['money']['amount'],
            'money_change': resources['money']['production'] - resources['money']['consumption'],
            'resources': resources,
            
            # Population
            'population': demographics['total_population'],
            'unemployment_rate': demographics['unemployment_rate'],
            'satisfaction': demographics['average_satisfaction'],
            'demographics': demographics,
            
            # Infrastructure
            'total_buildings': len(buildings),
            'building_types': self._count_building_types(buildings),
            'needs': self.population.needs,
            
            # Statistics
            'statistics': self.statistics,
            'alerts': self.get_recent_alerts()
        }
    
    def _count_building_types(self, buildings: List[Building]) -> Dict[str, int]:
        """Count buildings by type"""
        counts = {}
        for building in buildings:
            building_type = building.building_type.value
            counts[building_type] = counts.get(building_type, 0) + 1
        return counts
    
    def save_game(self, filepath: str) -> bool:
        """Save game state to file"""
        try:
            import json
            import os
            
            save_data = {
                'version': '1.0',
                'turn': self.turn,
                'difficulty': self.difficulty,
                'statistics': self.statistics,
                'alerts': self.alerts,
                'city_level': self.city_level,
                
                # Map data
                'map': {
                    'width': self.city_map.width,
                    'height': self.city_map.height,
                    'tiles': []
                },
                
                # Economy data
                'economy': self.economy.save_to_dict(),
                
                # Population data
                'population': self.population.save_to_dict()
            }
            
            # Save tile data
            for x in range(self.city_map.width):
                for y in range(self.city_map.height):
                    tile = self.city_map.get_tile(x, y)
                    tile_data = {
                        'x': x,
                        'y': y,
                        'terrain_type': tile.terrain_type.value,
                        'is_occupied': tile.is_occupied,
                        'building': None
                    }
                    
                    if tile.building:
                        tile_data['building'] = {
                            'name': tile.building.name,
                            'building_type': tile.building.building_type.value,
                            'cost': tile.building.cost,
                            'effects': tile.building.effects,
                            'rotation': tile.building.rotation
                        }
                    
                    save_data['map']['tiles'].append(tile_data)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            filename = os.path.basename(filepath)
            self.add_alert(f"Gra zapisana jako {filename}")
            return True
            
        except Exception as e:
            self.add_alert(f"Błąd zapisu gry: {str(e)}", priority="warning")
            return False
    
    def load_game(self, filepath: str) -> bool:
        """Load game state from file"""
        try:
            import json
            import os
            from .city_map import CityMap, TerrainType
            from .tile import Building, BuildingType
            
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Load basic game state
            self.turn = save_data.get('turn', 0)
            self.difficulty = save_data.get('difficulty', 'Normal')
            self.statistics = save_data.get('statistics', {})
            self.alerts = save_data.get('alerts', [])
            self.city_level = save_data.get('city_level', 1)
            
            # Load map
            map_data = save_data.get('map', {})
            self.city_map = CityMap(map_data.get('width', 60), map_data.get('height', 60))
            
            # Load tiles
            for tile_data in map_data.get('tiles', []):
                x, y = tile_data['x'], tile_data['y']
                tile = self.city_map.get_tile(x, y)
                
                if tile:
                    tile.terrain_type = TerrainType(tile_data['terrain_type'])
                    tile.is_occupied = tile_data['is_occupied']
                    
                    if tile_data['building']:
                        building_data = tile_data['building']
                        building = Building(
                            building_data['name'],
                            BuildingType(building_data['building_type']),
                            building_data['cost'],
                            building_data['effects']
                        )
                        building.rotation = building_data.get('rotation', 0)
                        tile.building = building
            
            # Load economy
            if 'economy' in save_data:
                self.economy.load_from_dict(save_data['economy'])
            
            # Load population
            if 'population' in save_data:
                self.population.load_from_dict(save_data['population'])
            
            filename = os.path.basename(filepath)
            self.add_alert(f"Gra wczytana: {filename}")
            return True
            
        except Exception as e:
            self.add_alert(f"Błąd wczytywania gry: {str(e)}", priority="warning")
            return False
    
    def update_city_level(self):
        """Update city level based on population"""
        current_pop = self.population.get_total_population()
        next_level = self.city_level + 1
        
        if next_level in self.level_requirements:
            if current_pop >= self.level_requirements[next_level]:
                self.city_level = next_level
                self.add_alert(f"🎉 Miasto osiągnęło poziom {next_level}!")
                return True
        return False

    def get_next_level_requirement(self) -> int:
        """Get population requirement for next level"""
        next_level = self.city_level + 1
        return self.level_requirements.get(next_level, 0)

    def is_building_unlocked(self, building: Building) -> tuple[bool, str]:
        """Check if a building is unlocked based on game conditions"""
        # Basic buildings are always available
        basic_buildings = [
            BuildingType.ROAD,
            BuildingType.ROAD_CURVE,
            BuildingType.SIDEWALK,
            BuildingType.HOUSE,
            BuildingType.SHOP
        ]
        if building.building_type in basic_buildings:
            return True, "OK"
        if not hasattr(building, 'unlock_condition') or not building.unlock_condition:
            return True, "OK"
        conditions = building.unlock_condition
        # Check city level requirement
        if 'city_level' in conditions:
            if self.city_level < conditions['city_level']:
                return False, f"Od poziomu miasta: {conditions['city_level']}"
        # Check population requirement
        if 'population' in conditions:
            current_pop = self.population.get_total_population()
            if current_pop < conditions['population']:
                return False, f"Wymagana populacja: {conditions['population']}"
        
        # Check technology requirement
        if 'technology' in conditions:
            required_tech = conditions['technology']
            if required_tech not in [tech.id for tech in self.technology_manager.get_researched_technologies()]:
                tech = self.technology_manager.technologies.get(required_tech)
                tech_name = tech.name if tech else required_tech
                return False, f"Wymagana technologia: {tech_name}"
        
        return True, "OK"
    
    # Technology management methods
    def start_research(self, tech_id: str, investment: int = 0) -> tuple[bool, str]:
        """Start researching a technology"""
        can_research, reason = self.technology_manager.can_research(tech_id)
        if not can_research:
            return False, reason
        
        # Check if we can afford the investment
        if investment > 0 and not self.economy.can_afford(investment):
            return False, f"Cannot afford research investment of ${investment:,}"
        
        # Deduct investment cost
        if investment > 0:
            self.economy.spend_money(investment)
        
        success = self.technology_manager.start_research(tech_id, investment)
        if success:
            tech = self.technology_manager.technologies[tech_id]
            self.add_alert(f"🔬 Started researching: {tech.name}")
            if investment > 0:
                self.add_alert(f"💰 Research investment: ${investment:,}")
        
        return success, "Research started" if success else "Failed to start research"
    
    def get_available_technologies(self):
        """Get technologies available for research"""
        return self.technology_manager.get_available_technologies()
    
    def get_researched_technologies(self):
        """Get completed technologies"""
        return self.technology_manager.get_researched_technologies()
    
    def get_current_research(self):
        """Get currently researched technology"""
        if self.technology_manager.current_research:
            return self.technology_manager.technologies[self.technology_manager.current_research]
        return None
    
    def get_technology_effects(self):
        """Get cumulative effects of all researched technologies"""
        return self.technology_manager.get_technology_effects()
    
    # Trade management methods
    def get_trade_offers(self, good_type=None):
        """Get available trade offers"""
        return self.trade_manager.get_available_offers(good_type)
    
    def accept_trade_offer(self, offer_id: str) -> tuple[bool, str]:
        """Accept a trade offer"""
        success, message = self.trade_manager.accept_offer(offer_id)
        if success:
            self.statistics['trades_completed'] += 1
            self.add_alert(f"📦 {message}")
        return success, message
    
    def create_trade_contract(self, city_id: str, good_type, quantity_per_turn: int, 
                            price_per_unit: float, duration_turns: int, is_buying: bool) -> tuple[bool, str]:
        """Create a long-term trade contract"""
        return self.trade_manager.create_contract(city_id, good_type, quantity_per_turn, 
                                                price_per_unit, duration_turns, is_buying)
    
    def get_trade_statistics(self):
        """Get trade statistics"""
        return self.trade_manager.get_trade_statistics()
    
    def get_trading_cities(self):
        """Get all trading cities"""
        return self.trade_manager.trading_cities
    
    # Achievement management methods
    def get_achievements_by_category(self, category):
        """Get achievements by category"""
        return self.achievement_manager.get_achievements_by_category(category)
    
    def get_unlocked_achievements(self):
        """Get unlocked achievements"""
        return self.achievement_manager.get_unlocked_achievements()
    
    def get_locked_achievements(self, include_hidden=False):
        """Get locked achievements"""
        return self.achievement_manager.get_locked_achievements(include_hidden)
    
    def get_achievement_statistics(self):
        """Get achievement statistics"""
        return self.achievement_manager.get_achievement_statistics()
    
    def get_achievement_notifications(self):
        """Get and clear achievement notifications"""
        return self.achievement_manager.get_notifications()
    
    def get_all_achievements(self):
        """Get all achievements"""
        return list(self.achievement_manager.achievements.values())
