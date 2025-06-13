from typing import Dict, List
from dataclasses import dataclass, field
import json

@dataclass
class ResourceData:
    """Represents a single resource type"""
    name: str
    amount: float
    max_capacity: float = float('inf')
    production_rate: float = 0.0
    consumption_rate: float = 0.0
    price: float = 1.0  # For trading

class Economy:
    """Manages city's economy and resources"""
    
    def __init__(self, initial_money: float = 50000):
        self.resources = {
            # Basic resources
            'money': ResourceData('Money', initial_money, max_capacity=float('inf')),
            'energy': ResourceData('Energy', 100, max_capacity=1000, price=2.0),
            'water': ResourceData('Water', 100, max_capacity=1000, price=1.5),
            'materials': ResourceData('Materials', 50, max_capacity=500, price=3.0),
            'food': ResourceData('Food', 80, max_capacity=800, price=2.5),
            'luxury_goods': ResourceData('Luxury Goods', 20, max_capacity=200, price=5.0),
            
            # Derived metrics
            'population': ResourceData('Population', 0, price=0),
            'happiness': ResourceData('Happiness', 50, max_capacity=100, price=0),
            'education': ResourceData('Education', 0, max_capacity=100, price=0),
            'health': ResourceData('Health', 50, max_capacity=100, price=0),
            'safety': ResourceData('Safety', 50, max_capacity=100, price=0),
            'environment': ResourceData('Environment', 50, max_capacity=100, price=0),
        }
        
        self.tax_rates = {
            'residential': 0.05,  # 5% tax on residential income
            'commercial': 0.08,   # 8% tax on commercial income
            'industrial': 0.10,   # 10% tax on industrial income
        }
        
        self.expenses = {
            'maintenance': 0,     # Building maintenance costs
            'salaries': 0,        # Public service salaries
            'utilities': 0,       # City utilities
        }
        
        self.history: List[Dict] = []  # Resource history for reports
        
    def get_resource(self, resource_name: str) -> ResourceData:
        """Get resource by name"""
        return self.resources.get(resource_name, ResourceData(resource_name, 0))
    
    def get_resource_amount(self, resource_name: str) -> float:
        """Get current amount of a resource"""
        return self.resources.get(resource_name, ResourceData(resource_name, 0)).amount
    
    def modify_resource(self, resource_name: str, amount: float) -> bool:
        """Modify resource amount, returns True if successful"""
        if resource_name not in self.resources:
            return False
            
        resource = self.resources[resource_name]
        new_amount = resource.amount + amount
        
        # Check constraints
        if new_amount < 0:
            return False
        if new_amount > resource.max_capacity:
            new_amount = resource.max_capacity
            
        resource.amount = new_amount
        return True
    
    def can_afford(self, cost: float) -> bool:
        """Check if city can afford the cost"""
        return self.get_resource_amount('money') >= cost
    
    def spend_money(self, amount: float) -> bool:
        """Spend money if available"""
        if self.can_afford(amount):
            self.modify_resource('money', -amount)
            return True
        return False
    
    def earn_money(self, amount: float):
        """Add money to treasury"""
        self.modify_resource('money', amount)
    
    def calculate_taxes(self, buildings: List, population_manager=None) -> float:
        """Calculate tax income from buildings and working population (boosted, extra for commercial/industrial)."""
        total_tax = 0
        employed_population = 0
        if population_manager:
            employed_population = sum(
                group.count for social, group in population_manager.groups.items()
                if hasattr(group, 'employment_rate') and group.employment_rate > 0.1 and social.name not in ['STUDENT', 'UNEMPLOYED']
            )
        for building in buildings:
            if not building or not hasattr(building, 'building_type'):
                continue
            building_type = building.building_type.value
            # Wyższy dochód z komercyjnych i przemysłowych
            if 'commercial' in building_type or 'shop' in building_type or 'mall' in building_type:
                base_income = building.cost * 0.025  # 2.5% dla komercyjnych
                total_tax += base_income * self.tax_rates['commercial']
            elif 'industrial' in building_type or 'factory' in building_type:
                base_income = building.cost * 0.022  # 2.2% dla przemysłowych
                total_tax += base_income * self.tax_rates['industrial']
            elif 'residential' in building_type or 'house' in building_type or 'apartment' in building_type:
                base_income = building.cost * 0.018
                total_tax += base_income * self.tax_rates['residential']
            else:
                base_income = building.cost * 0.018
                total_tax += base_income * self.tax_rates['residential']
        # Większy podatek od zatrudnionych mieszkańców (np. 18 na osobę * stawka podatku mieszkaniowego)
        total_tax += employed_population * 18 * self.tax_rates['residential']
        return total_tax
    
    def calculate_expenses(self, buildings: List, population_manager=None) -> float:
        """Delikatnie zwiększam koszty utrzymania parków, szkół, szpitali, uniwersytetów, policji, straży pożarnej."""
        total_expenses = 0
        for building in buildings:
            if not building:
                continue
            building_type = building.building_type.value
            # Delikatnie wyższy koszt utrzymania dla usług publicznych
            if any(service in building_type for service in ['park', 'school', 'hospital', 'university', 'police', 'fire']):
                maintenance_cost = building.cost * 0.0012  # 0.12% dla usług publicznych
            else:
                maintenance_cost = building.cost * 0.0015  # 0.15% dla pozostałych
            total_expenses += maintenance_cost
            # Dodatkowe koszty dla publicznych (delikatnie wyższe)
            if any(service in building_type for service in ['hospital', 'school', 'university', 'police', 'fire']):
                total_expenses += building.cost * 0.0015  # 0.15% dodatkowo
        # Koszt mieszkańca
        if population_manager:
            total_pop = population_manager.get_total_population()
            total_expenses += total_pop * 0.3
        return total_expenses
    
    def update_turn(self, buildings: List, population_manager=None):
        """Update resources at the end of each turn"""
        # Calculate income and expenses
        tax_income = self.calculate_taxes(buildings, population_manager)
        total_expenses = self.calculate_expenses(buildings, population_manager)
        # Update money
        net_income = tax_income - total_expenses
        self.earn_money(net_income)
        # Update resource production/consumption
        self._update_resource_flows(buildings)
        # Store history for reports
        self._record_history()
    
    def _update_resource_flows(self, buildings: List):
        """Update resource production and consumption"""
        # Reset production/consumption rates
        for resource in self.resources.values():
            resource.production_rate = 0
            resource.consumption_rate = 0
        
        # Calculate from buildings
        for building in buildings:
            if not building or not hasattr(building, 'effects'):
                continue
                
            for effect, value in building.effects.items():
                if effect in self.resources:
                    if value > 0:
                        self.resources[effect].production_rate += value
                    else:
                        self.resources[effect].consumption_rate += abs(value)
        
        # Apply production/consumption
        for resource_name, resource in self.resources.items():
            if resource_name == 'money':  # Money handled separately
                continue
                
            net_change = resource.production_rate - resource.consumption_rate
            self.modify_resource(resource_name, net_change)
    
    def _record_history(self):
        """Record current state for historical analysis"""
        snapshot = {
            'turn': len(self.history) + 1,
            'resources': {name: res.amount for name, res in self.resources.items()},
            'tax_income': self.calculate_taxes([]),  # Would need actual buildings
            'expenses': sum(self.expenses.values())
        }
        self.history.append(snapshot)
        
        # Keep only last 100 turns
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_resource_summary(self) -> Dict:
        """Get summary of all resources"""
        return {
            name: {
                'amount': res.amount,
                'max_capacity': res.max_capacity,
                'production': res.production_rate,
                'consumption': res.consumption_rate,
                'price': res.price
            }
            for name, res in self.resources.items()
        }
    
    def save_to_dict(self) -> Dict:
        """Save economy state to dictionary"""
        return {
            'resources': {
                name: {
                    'name': res.name,
                    'amount': res.amount,
                    'max_capacity': res.max_capacity,
                    'production_rate': res.production_rate,
                    'consumption_rate': res.consumption_rate,
                    'price': res.price
                }
                for name, res in self.resources.items()
            },
            'tax_rates': self.tax_rates,
            'expenses': self.expenses,
            'history': self.history
        }
    
    def load_from_dict(self, data: Dict):
        """Load economy state from dictionary"""
        if 'resources' in data:
            for name, res_data in data['resources'].items():
                self.resources[name] = ResourceData(**res_data)
        
        if 'tax_rates' in data:
            self.tax_rates.update(data['tax_rates'])
            
        if 'expenses' in data:
            self.expenses.update(data['expenses'])
            
        if 'history' in data:
            self.history = data['history']

