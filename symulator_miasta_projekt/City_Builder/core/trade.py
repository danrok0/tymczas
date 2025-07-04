"""
System handlu międzymiastowego dla City Builder
Implementuje handel z sąsiednimi miastami, negocjacje cen i umowy handlowe
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random
import time

class TradeGoodType(Enum):
    FOOD = "food"
    MATERIALS = "materials"
    ENERGY = "energy"
    LUXURY = "luxury"
    TECHNOLOGY = "technology"
    SERVICES = "services"

class RelationshipStatus(Enum):
    HOSTILE = "hostile"
    UNFRIENDLY = "unfriendly"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    ALLIED = "allied"

@dataclass
class TradeGood:
    """Reprezentuje towar do handlu"""
    type: TradeGoodType
    name: str
    base_price: float
    volatility: float  # Jak bardzo cena może się zmieniać (0.0-1.0)
    current_price: float = 0
    demand_modifier: float = 1.0
    supply_modifier: float = 1.0
    
    def __post_init__(self):
        if self.current_price == 0:
            self.current_price = self.base_price

@dataclass
class TradeOffer:
    """Oferta handlowa"""
    id: str
    city_id: str
    good_type: TradeGoodType
    quantity: int
    price_per_unit: float
    is_buying: bool  # True = miasto kupuje, False = miasto sprzedaje
    expires_turn: int
    relationship_bonus: float = 0.0

@dataclass
class TradeContract:
    """Kontrakt handlowy"""
    id: str
    city_id: str
    good_type: TradeGoodType
    quantity_per_turn: int
    price_per_unit: float
    duration_turns: int
    remaining_turns: int
    is_buying: bool

class TradingCity:
    """Reprezentuje miasto handlowe"""
    
    def __init__(self, city_id: str, name: str, specialization: TradeGoodType):
        self.city_id = city_id
        self.name = name
        self.specialization = specialization
        self.relationship = RelationshipStatus.NEUTRAL
        self.relationship_points = 0  # -100 do +100
        self.trade_volume = 0
        self.reputation = 50  # 0-100
        
        # Preferencje handlowe
        self.preferred_goods = [specialization]
        self.avoided_goods = []
        
        # Modyfikatory cen
        self.price_modifiers = {good_type: 1.0 for good_type in TradeGoodType}
        self.price_modifiers[specialization] = 0.8  # Specjalizacja = tańsze
        
        # Historia handlu
        self.trade_history = []
        
    def update_relationship(self, points_change: int):
        """Aktualizuje relacje z miastem"""
        self.relationship_points = max(-100, min(100, self.relationship_points + points_change))
        
        # Aktualizuj status relacji
        if self.relationship_points >= 80:
            self.relationship = RelationshipStatus.ALLIED
        elif self.relationship_points >= 40:
            self.relationship = RelationshipStatus.FRIENDLY
        elif self.relationship_points >= -20:
            self.relationship = RelationshipStatus.NEUTRAL
        elif self.relationship_points >= -60:
            self.relationship = RelationshipStatus.UNFRIENDLY
        else:
            self.relationship = RelationshipStatus.HOSTILE
    
    def get_price_modifier(self, good_type: TradeGoodType) -> float:
        """Zwraca modyfikator ceny dla danego towaru"""
        base_modifier = self.price_modifiers.get(good_type, 1.0)
        
        # Bonus za dobre relacje
        relationship_bonus = {
            RelationshipStatus.HOSTILE: 1.5,
            RelationshipStatus.UNFRIENDLY: 1.2,
            RelationshipStatus.NEUTRAL: 1.0,
            RelationshipStatus.FRIENDLY: 0.9,
            RelationshipStatus.ALLIED: 0.8
        }
        
        return base_modifier * relationship_bonus[self.relationship]

class TradeManager:
    """Zarządza systemem handlu międzymiastowego"""
    
    def __init__(self):
        self.trading_cities = {}
        self.trade_goods = {}
        self.active_offers = []
        self.active_contracts = []
        self.trade_history = []
        self.current_turn = 0
        
        self._initialize_trade_goods()
        self._initialize_trading_cities()
    
    def _initialize_trade_goods(self):
        """Inicjalizuje dostępne towary handlowe"""
        goods_data = [
            ("food", "Żywność", 10, 0.3),
            ("grain", "Zboże", 8, 0.2),
            ("meat", "Mięso", 15, 0.4),
            ("materials", "Materiały budowlane", 20, 0.25),
            ("steel", "Stal", 35, 0.3),
            ("wood", "Drewno", 12, 0.2),
            ("energy", "Energia", 25, 0.4),
            ("oil", "Ropa", 40, 0.5),
            ("coal", "Węgiel", 18, 0.3),
            ("luxury", "Towary luksusowe", 50, 0.6),
            ("electronics", "Elektronika", 80, 0.4),
            ("jewelry", "Biżuteria", 120, 0.7),
            ("technology", "Technologia", 100, 0.3),
            ("software", "Oprogramowanie", 60, 0.2),
            ("research", "Badania", 150, 0.4),
            ("services", "Usługi", 30, 0.2),
            ("tourism", "Turystyka", 25, 0.3),
            ("finance", "Finanse", 45, 0.25)
        ]
        
        for good_id, name, base_price, volatility in goods_data:
            # Określ typ na podstawie nazwy
            if good_id in ["food", "grain", "meat"]:
                good_type = TradeGoodType.FOOD
            elif good_id in ["materials", "steel", "wood"]:
                good_type = TradeGoodType.MATERIALS
            elif good_id in ["energy", "oil", "coal"]:
                good_type = TradeGoodType.ENERGY
            elif good_id in ["luxury", "electronics", "jewelry"]:
                good_type = TradeGoodType.LUXURY
            elif good_id in ["technology", "software", "research"]:
                good_type = TradeGoodType.TECHNOLOGY
            else:
                good_type = TradeGoodType.SERVICES
            
            self.trade_goods[good_id] = TradeGood(
                type=good_type,
                name=name,
                base_price=base_price,
                volatility=volatility
            )
    
    def _initialize_trading_cities(self):
        """Inicjalizuje miasta handlowe"""
        cities_data = [
            ("agropolis", "Agropolis", TradeGoodType.FOOD),
            ("steelburg", "Steelburg", TradeGoodType.MATERIALS),
            ("energyville", "Energyville", TradeGoodType.ENERGY),
            ("luxuria", "Luxuria", TradeGoodType.LUXURY),
            ("techcity", "TechCity", TradeGoodType.TECHNOLOGY),
            ("servicetown", "ServiceTown", TradeGoodType.SERVICES)
        ]
        
        for city_id, name, specialization in cities_data:
            self.trading_cities[city_id] = TradingCity(city_id, name, specialization)
    
    def update_turn(self):
        """Aktualizuje system handlu na koniec tury"""
        self.current_turn += 1
        
        # Aktualizuj ceny towarów
        self._update_market_prices()
        
        # Wygeneruj nowe oferty
        self._generate_trade_offers()
        
        # Usuń wygasłe oferty
        self._remove_expired_offers()
        
        # Wykonaj kontrakty
        self._execute_contracts()
        
        # Aktualizuj relacje
        self._update_relationships()
    
    def _update_market_prices(self):
        """Aktualizuje ceny rynkowe towarów"""
        for good in self.trade_goods.values():
            # Losowa zmiana ceny w ramach volatility
            price_change = random.uniform(-good.volatility, good.volatility)
            new_price = good.current_price * (1 + price_change)
            
            # Ograniczenia cenowe (50%-200% ceny bazowej)
            min_price = good.base_price * 0.5
            max_price = good.base_price * 2.0
            good.current_price = max(min_price, min(max_price, new_price))
    
    def _generate_trade_offers(self):
        """Generuje nowe oferty handlowe"""
        for city in self.trading_cities.values():
            # Każde miasto ma 30% szansy na nową ofertę
            if random.random() < 0.3:
                self._create_city_offer(city)
    
    def _create_city_offer(self, city: TradingCity):
        """Tworzy ofertę dla konkretnego miasta"""
        # Wybierz towar
        available_goods = list(self.trade_goods.keys())
        good_id = random.choice(available_goods)
        good = self.trade_goods[good_id]
        
        # Określ czy miasto kupuje czy sprzedaje
        is_buying = random.choice([True, False])
        
        # Miasto częściej sprzedaje swoją specjalizację
        if good.type == city.specialization:
            is_buying = random.random() < 0.3  # 30% szansy na kupowanie specjalizacji
        
        # Ilość i cena
        quantity = random.randint(50, 500)
        base_price = good.current_price
        price_modifier = city.get_price_modifier(good.type)
        
        if is_buying:
            # Miasto kupuje - oferuje wyższą cenę
            price_per_unit = base_price * price_modifier * random.uniform(1.05, 1.2)
        else:
            # Miasto sprzedaje - oferuje niższą cenę
            price_per_unit = base_price * price_modifier * random.uniform(0.8, 0.95)
        
        # Czas wygaśnięcia
        expires_turn = self.current_turn + random.randint(3, 8)
        
        offer = TradeOffer(
            id=f"{city.city_id}_{good_id}_{self.current_turn}_{len(self.active_offers)}",
            city_id=city.city_id,
            good_type=good.type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            is_buying=is_buying,
            expires_turn=expires_turn
        )
        
        self.active_offers.append(offer)
    
    def _remove_expired_offers(self):
        """Usuwa wygasłe oferty"""
        self.active_offers = [
            offer for offer in self.active_offers 
            if offer.expires_turn > self.current_turn
        ]
    
    def _execute_contracts(self):
        """Wykonuje aktywne kontrakty"""
        completed_contracts = []
        
        for contract in self.active_contracts:
            contract.remaining_turns -= 1
            
            # Tutaj można dodać logikę automatycznego wykonania kontraktu
            # (transfer zasobów, płatności itp.)
            
            if contract.remaining_turns <= 0:
                completed_contracts.append(contract)
        
        # Usuń ukończone kontrakty
        for contract in completed_contracts:
            self.active_contracts.remove(contract)
    
    def _update_relationships(self):
        """Aktualizuje relacje z miastami"""
        for city in self.trading_cities.values():
            # Naturalna degradacja relacji (bardzo powolna)
            if city.relationship_points > 0:
                city.update_relationship(-1)
            elif city.relationship_points < 0:
                city.update_relationship(1)
    
    def get_available_offers(self, good_type: TradeGoodType = None) -> List[TradeOffer]:
        """Zwraca dostępne oferty handlowe"""
        offers = self.active_offers
        if good_type:
            offers = [offer for offer in offers if offer.good_type == good_type]
        return sorted(offers, key=lambda x: x.price_per_unit)
    
    def accept_offer(self, offer_id: str) -> Tuple[bool, str]:
        """Akceptuje ofertę handlową"""
        offer = next((o for o in self.active_offers if o.id == offer_id), None)
        if not offer:
            return False, "Oferta nie istnieje"
        
        # Usuń ofertę z listy
        self.active_offers.remove(offer)
        
        # Aktualizuj relacje
        city = self.trading_cities[offer.city_id]
        city.update_relationship(5)  # Bonus za handel
        city.trade_volume += offer.quantity * offer.price_per_unit
        
        # Dodaj do historii
        self.trade_history.append({
            'turn': self.current_turn,
            'city': city.name,
            'good_type': offer.good_type.value,
            'quantity': offer.quantity,
            'price': offer.price_per_unit,
            'total_value': offer.quantity * offer.price_per_unit,
            'is_buying': offer.is_buying
        })
        
        return True, f"Handel z {city.name} zakończony sukcesem"
    
    def create_contract(self, city_id: str, good_type: TradeGoodType, 
                       quantity_per_turn: int, price_per_unit: float, 
                       duration_turns: int, is_buying: bool) -> Tuple[bool, str]:
        """Tworzy długoterminowy kontrakt handlowy"""
        if city_id not in self.trading_cities:
            return False, "Nieznane miasto"
        
        city = self.trading_cities[city_id]
        
        # Sprawdź relacje (potrzebne przynajmniej neutralne)
        if city.relationship == RelationshipStatus.HOSTILE:
            return False, "Miasto odmawia handlu z powodu wrogich relacji"
        
        contract = TradeContract(
            id=f"contract_{city_id}_{good_type.value}_{self.current_turn}",
            city_id=city_id,
            good_type=good_type,
            quantity_per_turn=quantity_per_turn,
            price_per_unit=price_per_unit,
            duration_turns=duration_turns,
            remaining_turns=duration_turns,
            is_buying=is_buying
        )
        
        self.active_contracts.append(contract)
        
        # Bonus do relacji za długoterminowy kontrakt
        city.update_relationship(10)
        
        return True, f"Kontrakt z {city.name} podpisany na {duration_turns} tur"
    
    def get_trade_statistics(self) -> Dict:
        """Zwraca statystyki handlowe"""
        total_trade_value = sum(trade['total_value'] for trade in self.trade_history)
        
        # Handel według miast
        city_stats = {}
        for trade in self.trade_history:
            city = trade['city']
            if city not in city_stats:
                city_stats[city] = {'trades': 0, 'value': 0}
            city_stats[city]['trades'] += 1
            city_stats[city]['value'] += trade['total_value']
        
        # Handel według towarów
        good_stats = {}
        for trade in self.trade_history:
            good = trade['good_type']
            if good not in good_stats:
                good_stats[good] = {'trades': 0, 'value': 0}
            good_stats[good]['trades'] += 1
            good_stats[good]['value'] += trade['total_value']
        
        return {
            'total_trades': len(self.trade_history),
            'total_value': total_trade_value,
            'active_contracts': len(self.active_contracts),
            'active_offers': len(self.active_offers),
            'city_stats': city_stats,
            'good_stats': good_stats,
            'relationships': {
                city.name: {
                    'status': city.relationship.value,
                    'points': city.relationship_points,
                    'trade_volume': city.trade_volume
                }
                for city in self.trading_cities.values()
            }
        }
    
    def save_to_dict(self) -> Dict:
        """Zapisuje stan handlu do słownika"""
        return {
            'current_turn': self.current_turn,
            'trade_history': self.trade_history,
            'trading_cities': {
                city_id: {
                    'relationship_points': city.relationship_points,
                    'trade_volume': city.trade_volume,
                    'reputation': city.reputation
                }
                for city_id, city in self.trading_cities.items()
            },
            'active_contracts': [
                {
                    'id': contract.id,
                    'city_id': contract.city_id,
                    'good_type': contract.good_type.value,
                    'quantity_per_turn': contract.quantity_per_turn,
                    'price_per_unit': contract.price_per_unit,
                    'duration_turns': contract.duration_turns,
                    'remaining_turns': contract.remaining_turns,
                    'is_buying': contract.is_buying
                }
                for contract in self.active_contracts
            ]
        }
    
    def load_from_dict(self, data: Dict):
        """Wczytuje stan handlu ze słownika"""
        self.current_turn = data.get('current_turn', 0)
        self.trade_history = data.get('trade_history', [])
        
        # Wczytaj miasta
        cities_data = data.get('trading_cities', {})
        for city_id, city_data in cities_data.items():
            if city_id in self.trading_cities:
                city = self.trading_cities[city_id]
                city.relationship_points = city_data.get('relationship_points', 0)
                city.trade_volume = city_data.get('trade_volume', 0)
                city.reputation = city_data.get('reputation', 50)
                city.update_relationship(0)  # Aktualizuj status relacji
        
        # Wczytaj kontrakty
        contracts_data = data.get('active_contracts', [])
        self.active_contracts = []
        for contract_data in contracts_data:
            contract = TradeContract(
                id=contract_data['id'],
                city_id=contract_data['city_id'],
                good_type=TradeGoodType(contract_data['good_type']),
                quantity_per_turn=contract_data['quantity_per_turn'],
                price_per_unit=contract_data['price_per_unit'],
                duration_turns=contract_data['duration_turns'],
                remaining_turns=contract_data['remaining_turns'],
                is_buying=contract_data['is_buying']
            )
            self.active_contracts.append(contract) 