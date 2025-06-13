from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random

class SocialClass(Enum):
    WORKER = "worker"
    MIDDLE_CLASS = "middle_class"
    UPPER_CLASS = "upper_class"
    STUDENT = "student"
    UNEMPLOYED = "unemployed"

@dataclass
class PopulationGroup:
    """Represents a group of population with similar characteristics"""
    social_class: SocialClass
    count: int
    employment_rate: float = 0.0
    satisfaction: float = 50.0  # 0-100 scale
    income: float = 0.0
    age_distribution: Dict[str, int] = None  # young, adult, elderly
    
    def __post_init__(self):
        if self.age_distribution is None:
            self.age_distribution = {"young": 30, "adult": 50, "elderly": 20}

class PopulationManager:
    """Manages city population dynamics"""
    
    def __init__(self):
        # Population groups with their characteristics
        self.population_groups = {
            'workers': {'size': 100, 'income': 1000, 'tax_rate': 0.2, 'satisfaction': 0.5},
            'middle_class': {'size': 50, 'income': 2000, 'tax_rate': 0.25, 'satisfaction': 0.5},
            'elite': {'size': 10, 'income': 5000, 'tax_rate': 0.3, 'satisfaction': 0.5}
        }
        
        # Population growth parameters - adjusted for more natural growth
        self.birth_rate = 0.025  # Increased from 0.015 to 0.025 (2.5% natural growth)
        self.death_rate = 0.002  # Decreased from 0.003 to 0.002 (0.2% death rate)
        self.migration_factor = 0.01  # Decreased from 0.02 to 0.01 (1% migration impact)
        
        # Housing and satisfaction parameters - more forgiving
        self.housing_satisfaction_threshold = 0.2  # Decreased from 0.3 to 0.2
        self.satisfaction_multiplier = 0.8  # Increased from 0.5 to 0.8
        self.min_satisfaction = 0.1  # Decreased from 0.2 to 0.1
        self.max_population_decline = 0.01  # Decreased from 0.02 to 0.01 (max 1% decline per turn)
        
        # Initialize needs
        self.needs = {
            'housing': 0.0,
            'jobs': 0.0,
            'services': 0.0,
            'entertainment': 0.0
        }
        
        # Initialize statistics
        self.statistics = {
            'total_population': 0,
            'unemployment_rate': 0.0,
            'average_satisfaction': 0.0,
            'population_growth': 0.0
        }
        
        self.groups = {
            SocialClass.WORKER: PopulationGroup(
                SocialClass.WORKER, 150,
                employment_rate=0.8, satisfaction=40.0, income=2000
            ),
            SocialClass.MIDDLE_CLASS: PopulationGroup(
                SocialClass.MIDDLE_CLASS, 75,
                employment_rate=0.85, satisfaction=60.0, income=4000
            ),
            SocialClass.UPPER_CLASS: PopulationGroup(
                SocialClass.UPPER_CLASS, 15,
                employment_rate=0.7, satisfaction=70.0, income=8000
            ),
            SocialClass.STUDENT: PopulationGroup(
                SocialClass.STUDENT, 30,
                employment_rate=0.3, satisfaction=55.0, income=500
            ),
            SocialClass.UNEMPLOYED: PopulationGroup(
                SocialClass.UNEMPLOYED, 20,
                employment_rate=0.0, satisfaction=20.0, income=800
            )
        }
        
        self.needs = {
            'housing': {'current': 0, 'demand': 0, 'satisfaction': 50},
            'jobs': {'current': 0, 'demand': 0, 'satisfaction': 50},
            'healthcare': {'current': 0, 'demand': 0, 'satisfaction': 50},
            'education': {'current': 0, 'demand': 0, 'satisfaction': 50},
            'safety': {'current': 0, 'demand': 0, 'satisfaction': 50},
            'entertainment': {'current': 0, 'demand': 0, 'satisfaction': 50},
            'transport': {'current': 0, 'demand': 0, 'satisfaction': 50}
        }
        
    def get_total_population(self) -> int:
        """Get total population count"""
        return sum(group.count for group in self.groups.values())
    
    def get_unemployment_rate(self) -> float:
        """Calculate unemployment rate"""
        total_workforce = sum(
            group.count for group in self.groups.values() 
            if group.social_class != SocialClass.STUDENT
        )
        unemployed = self.groups[SocialClass.UNEMPLOYED].count
        
        return (unemployed / total_workforce) * 100 if total_workforce > 0 else 0
    
    def get_average_satisfaction(self) -> float:
        """Calculate weighted average satisfaction"""
        total_pop = self.get_total_population()
        if total_pop == 0:
            return 50.0
            
        weighted_satisfaction = sum(
            group.count * group.satisfaction for group in self.groups.values()
        )
        return weighted_satisfaction / total_pop
    
    def calculate_needs(self, buildings: List):
        """Calculate population needs based on current infrastructure"""
        total_pop = self.get_total_population()
        
        if total_pop == 0:
            return
        
        # Reset current supply
        for need in self.needs.values():
            need['current'] = 0
        
        # Calculate supply from buildings
        for building in buildings:
            if not building or not hasattr(building, 'effects'):
                continue
                
            effects = building.effects
            building_type = building.building_type.value
            
            # Housing supply
            if 'population' in effects:
                self.needs['housing']['current'] += effects['population']
            
            # Jobs supply  
            if 'jobs' in effects:
                self.needs['jobs']['current'] += effects['jobs']
            
            # Healthcare supply
            if 'health' in effects:
                self.needs['healthcare']['current'] += effects['health']
            
            # Education supply
            if 'education' in effects:
                self.needs['education']['current'] += effects['education']
            
            # Safety supply
            if 'safety' in effects:
                self.needs['safety']['current'] += effects['safety']
            
            # Entertainment supply
            if 'happiness' in effects and ('park' in building_type or 'stadium' in building_type):
                self.needs['entertainment']['current'] += effects['happiness']
            
            # Transport supply
            if 'traffic' in effects or 'walkability' in effects:
                self.needs['transport']['current'] += effects.get('traffic', 0) + effects.get('walkability', 0)
        
        # Calculate demand based on population
        self.needs['housing']['demand'] = total_pop
        self.needs['jobs']['demand'] = int(total_pop * 0.6)  # 60% need jobs
        self.needs['healthcare']['demand'] = int(total_pop * 0.3)  # 30% need healthcare
        self.needs['education']['demand'] = int(total_pop * 0.4)  # 40% need education
        self.needs['safety']['demand'] = int(total_pop * 0.5)  # 50% need safety
        self.needs['entertainment']['demand'] = int(total_pop * 0.2)  # 20% need entertainment
        self.needs['transport']['demand'] = int(total_pop * 0.7)  # 70% need transport
        
        # Calculate satisfaction for each need
        for need_name, need_data in self.needs.items():
            if need_data['demand'] > 0:
                ratio = need_data['current'] / need_data['demand']
                need_data['satisfaction'] = min(100, ratio * 100)
            else:
                need_data['satisfaction'] = 100
    
    def update_population_dynamics(self):
        """Update population through births, deaths, and migration"""
        total_pop = self.get_total_population()
        if total_pop == 0:
            return
            
        avg_satisfaction = self.get_average_satisfaction()
        
        # Housing satisfaction bonus - zwiększony wpływ na wzrost
        housing_satisfaction = self.needs['housing']['satisfaction']
        housing_bonus = max(0, (housing_satisfaction - 30) / 100)  # Obniżony próg z 50 na 30
        
        # Natural population change - adjusted by satisfaction
        satisfaction_multiplier = max(0.5, avg_satisfaction / 100)  # Zwiększony minimalny mnożnik z 0.2 na 0.5
        
        # Przyrost naturalny - zwiększony wpływ satysfakcji
        births = int(total_pop * self.birth_rate * satisfaction_multiplier * (1 + housing_bonus) * random.uniform(0.9, 1.1))
        deaths = int(total_pop * self.death_rate * (2 - satisfaction_multiplier) * random.uniform(0.9, 1.1))
        
        # Migracja - bardziej stabilna
        migration_rate = ((avg_satisfaction - 20) / 100 + housing_bonus) * self.migration_factor  # Obniżony próg z 30 na 20
        migration = int(total_pop * migration_rate * random.uniform(0.8, 1.2))
        
        net_change = births - deaths + migration
        
        # Zabezpieczenie przed drastycznym spadkiem
        if net_change < 0 and abs(net_change) > total_pop * 0.02:  # Zmniejszone z 5% na 2%
            net_change = -int(total_pop * 0.02)
        
        # Distribute changes across social classes
        self._distribute_population_change(net_change)
        
        # Update employment
        self._update_employment()
        
        # Update satisfaction based on needs
        self._update_satisfaction()
    
    def _distribute_population_change(self, net_change: int):
        """Distribute population change across social classes"""
        if net_change == 0:
            return
            
        total_pop = self.get_total_population()
        if total_pop == 0:
            return
            
        # Distribute proportionally with some randomness
        for social_class, group in self.groups.items():
            if social_class == SocialClass.UNEMPLOYED:
                continue  # Handle unemployment separately
                
            proportion = group.count / total_pop
            change = int(net_change * proportion * random.uniform(0.7, 1.3))
            
            new_count = max(0, group.count + change)
            group.count = new_count
    
    def _update_employment(self):
        """Update employment rates based on available jobs"""
        total_jobs = self.needs['jobs']['current']
        total_workforce = sum(
            group.count for group in self.groups.values()
            if group.social_class != SocialClass.STUDENT
        )
        
        if total_workforce == 0:
            return
            
        employment_ratio = min(1.0, total_jobs / total_workforce)
        
        # Update employment rates
        for social_class, group in self.groups.items():
            if social_class == SocialClass.STUDENT:
                continue
            elif social_class == SocialClass.UNEMPLOYED:
                # Some unemployed might find jobs
                jobs_found = int(group.count * employment_ratio * 0.1)  # 10% chance
                group.count = max(0, group.count - jobs_found)
                # Add them to working class
                self.groups[SocialClass.WORKER].count += jobs_found
            else:
                # Update employment rate
                base_rate = {
                    SocialClass.WORKER: 0.8,
                    SocialClass.MIDDLE_CLASS: 0.85,
                    SocialClass.UPPER_CLASS: 0.7
                }.get(social_class, 0.5)
                
                group.employment_rate = min(base_rate, employment_ratio)
    
    def _update_satisfaction(self):
        """Update satisfaction based on needs fulfillment"""
        for social_class, group in self.groups.items():
            # Base satisfaction from needs
            needs_satisfaction = []
            for need_name, need_data in self.needs.items():
                needs_satisfaction.append(need_data['satisfaction'])
            
            # Calculate average needs satisfaction
            if needs_satisfaction:
                avg_needs = sum(needs_satisfaction) / len(needs_satisfaction)
            else:
                avg_needs = 50
            
            # Różne klasy społeczne mają różne priorytety
            if social_class == SocialClass.WORKER:
                # Robotnicy priorytetowo patrzą na pracę i mieszkania
                priority_satisfaction = (
                    self.needs['jobs']['satisfaction'] * 0.4 +  # Zwiększone z 0.3
                    self.needs['housing']['satisfaction'] * 0.4 +  # Zwiększone z 0.3
                    avg_needs * 0.2  # Zmniejszone z 0.4
                )
            elif social_class == SocialClass.MIDDLE_CLASS:
                # Klasa średnia patrzy na edukację i bezpieczeństwo
                priority_satisfaction = (
                    self.needs['education']['satisfaction'] * 0.3 +  # Zwiększone z 0.25
                    self.needs['safety']['satisfaction'] * 0.3 +  # Zwiększone z 0.25
                    self.needs['housing']['satisfaction'] * 0.2 +
                    avg_needs * 0.2  # Zmniejszone z 0.3
                )
            elif social_class == SocialClass.UPPER_CLASS:
                # Klasa wyższa patrzy na rozrywkę i transport
                priority_satisfaction = (
                    self.needs['entertainment']['satisfaction'] * 0.4 +  # Zwiększone z 0.3
                    self.needs['transport']['satisfaction'] * 0.3 +  # Zwiększone z 0.2
                    avg_needs * 0.3  # Zmniejszone z 0.5
                )
            else:
                priority_satisfaction = avg_needs
            
            # Gładkie przejście satysfakcji (nie skrajne zmiany)
            new_satisfaction = group.satisfaction * 0.8 + priority_satisfaction * 0.2  # Zmienione proporcje
            
            # Upewnij się, że satysfakcja nie spada poniżej 20% i nie rośnie powyżej 100%
            group.satisfaction = max(20, min(100, new_satisfaction))  # Zwiększony minimalny poziom z 10 na 20
    
    def get_demographics(self) -> Dict:
        """Get demographic statistics"""
        return {
            'total_population': self.get_total_population(),
            'unemployment_rate': self.get_unemployment_rate(),
            'average_satisfaction': self.get_average_satisfaction(),
            'social_groups': {
                class_name.value: {
                    'count': group.count,
                    'employment_rate': group.employment_rate,
                    'satisfaction': group.satisfaction,
                    'income': group.income
                }
                for class_name, group in self.groups.items()
            },
            'needs': self.needs
        }
    
    def save_to_dict(self) -> Dict:
        """Save population state to dictionary"""
        return {
            'groups': {
                class_name.value: {
                    'social_class': group.social_class.value,
                    'count': group.count,
                    'employment_rate': group.employment_rate,
                    'satisfaction': group.satisfaction,
                    'income': group.income,
                    'age_distribution': group.age_distribution
                }
                for class_name, group in self.groups.items()
            },
            'needs': self.needs,
            'birth_rate': self.birth_rate,
            'death_rate': self.death_rate,
            'migration_factor': self.migration_factor
        }
    
    def load_from_dict(self, data: Dict):
        """Load population state from dictionary"""
        if 'groups' in data:
            for class_name, group_data in data['groups'].items():
                social_class = SocialClass(class_name)
                self.groups[social_class] = PopulationGroup(
                    social_class=social_class,
                    count=group_data['count'],
                    employment_rate=group_data['employment_rate'],
                    satisfaction=group_data['satisfaction'],
                    income=group_data['income'],
                    age_distribution=group_data.get('age_distribution')
                )
        
        if 'needs' in data:
            self.needs.update(data['needs'])
            
        if 'birth_rate' in data:
            self.birth_rate = data['birth_rate']
            
        if 'death_rate' in data:
            self.death_rate = data['death_rate']
            
        if 'migration_factor' in data:
            self.migration_factor = data['migration_factor']

    def add_instant_population(self, value: int):
        """Instantly add population to the WORKER group (default for new housing)."""
        if SocialClass.WORKER in self.groups:
            self.groups[SocialClass.WORKER].count += value
        else:
            # Fallback: add to any group
            for group in self.groups.values():
                group.count += value
                break
