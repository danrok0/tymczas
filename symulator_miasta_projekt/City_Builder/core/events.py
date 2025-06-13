import random
from typing import Dict, List, Optional

class Event:
    def __init__(self, title, description, effects, options=None, decision_effects=None):
        self.title = title
        self.description = description
        self.effects = effects  # Podstawowe efekty wydarzenia
        self.options = options or []
        self.decision_effects = decision_effects or {}  # Efekty różnych decyzji

class EventManager:
    def __init__(self):
        self.events = [
            # KATASTROFY
            Event(
                "Pożar w Dzielnicy",
                "Wybuchł pożar w dzielnicy mieszkalnej! Straż pożarna prosi o instrukcje.",
                {"population": -30, "satisfaction": -15},
                ["Wysłać wszystkie jednostki straży", "Ewakuować mieszkańców", "Zignorować"],
                {
                    "Wysłać wszystkie jednostki straży": {"money": -500, "population": -10, "satisfaction": 5},
                    "Ewakuować mieszkańców": {"population": -5, "satisfaction": -5, "money": -200},
                    "Zignorować": {"population": -50, "satisfaction": -25}
                }
            ),
            Event(
                "Epidemia Grypy",
                "W mieście wybuchła epidemia grypy. Szpitale są przepełnione.",
                {"population": -80, "satisfaction": -20},
                ["Wprowadzić kwarantannę", "Zwiększyć budżet szpitali", "Zignorować"],
                {
                    "Wprowadzić kwarantannę": {"money": -1000, "population": -20, "satisfaction": -10},
                    "Zwiększyć budżet szpitali": {"money": -1500, "population": -40, "satisfaction": 5},
                    "Zignorować": {"population": -120, "satisfaction": -35}
                }
            ),
            Event(
                "Trzęsienie Ziemi",
                "Słabe trzęsienie ziemi uszkodziło część infrastruktury miasta.",
                {"money": -2000, "satisfaction": -10},
                ["Natychmiastowe naprawy", "Stopniowa odbudowa", "Minimalne naprawy"],
                {
                    "Natychmiastowe naprawy": {"money": -3000, "satisfaction": 10},
                    "Stopniowa odbudowa": {"money": -1500, "satisfaction": 0},
                    "Minimalne naprawy": {"money": -500, "satisfaction": -15}
                }
            ),
            
            # KRYZYSY EKONOMICZNE
            Event(
                "Kryzys Ekonomiczny",
                "Globalny kryzys ekonomiczny dotarł do miasta. Bezrobocie rośnie.",
                {"money": -1500, "satisfaction": -20},
                ["Program pomocy społecznej", "Obniżyć podatki", "Nic nie robić"],
                {
                    "Program pomocy społecznej": {"money": -2000, "satisfaction": 15},
                    "Obniżyć podatki": {"money": -1000, "satisfaction": 10},
                    "Nic nie robić": {"satisfaction": -30}
                }
            ),
            Event(
                "Strajk Pracowników",
                "Pracownicy miejskich służb rozpoczęli strajk domagając się podwyżek.",
                {"satisfaction": -25},
                ["Spełnić żądania", "Negocjować kompromis", "Odrzucić żądania"],
                {
                    "Spełnić żądania": {"money": -2500, "satisfaction": 20},
                    "Negocjować kompromis": {"money": -1000, "satisfaction": 5},
                    "Odrzucić żądania": {"satisfaction": -40}
                }
            ),
            
            # WYDARZENIA POZYTYWNE
            Event(
                "Dotacja Rządowa",
                "Rząd przyznał miastu dotację na rozwój infrastruktury!",
                {"money": 3000, "satisfaction": 10},
                ["Zainwestować w transport", "Zbudować parki", "Odłożyć na później"],
                {
                    "Zainwestować w transport": {"money": 1000, "satisfaction": 15},
                    "Zbudować parki": {"money": 1500, "satisfaction": 20},
                    "Odłożyć na później": {"money": 3000, "satisfaction": 5}
                }
            ),
            Event(
                "Festiwal Miejski",
                "Organizatorzy proponują zorganizowanie wielkiego festiwalu w mieście.",
                {"satisfaction": 5},
                ["Sfinansować festiwal", "Częściowe wsparcie", "Odmówić"],
                {
                    "Sfinansować festiwal": {"money": -1500, "satisfaction": 25, "population": 20},
                    "Częściowe wsparcie": {"money": -500, "satisfaction": 15},
                    "Odmówić": {"satisfaction": -10}
                }
            ),
            Event(
                "Nowa Firma w Mieście",
                "Duża firma chce otworzyć oddział w waszym mieście.",
                {"population": 50, "satisfaction": 10},
                ["Dać ulgi podatkowe", "Standardowe warunki", "Odrzucić ofertę"],
                {
                    "Dać ulgi podatkowe": {"money": -500, "population": 100, "satisfaction": 15},
                    "Standardowe warunki": {"money": 500, "population": 50, "satisfaction": 10},
                    "Odrzucić ofertę": {"satisfaction": -5}
                }
            ),
            
            # WYDARZENIA SPOŁECZNE
            Event(
                "Protest Mieszkańców",
                "Mieszkańcy protestują przeciwko wysokim podatkom i niskiej jakości usług.",
                {"satisfaction": -30},
                ["Obniżyć podatki", "Poprawić usługi", "Zignorować protesty"],
                {
                    "Obniżyć podatki": {"money": -1000, "satisfaction": 20},
                    "Poprawić usługi": {"money": -2000, "satisfaction": 25},
                    "Zignorować protesty": {"satisfaction": -45, "population": -30}
                }
            ),
            Event(
                "Dzień Ziemi",
                "Mieszkańcy organizują obchody Dnia Ziemi i proszą o wsparcie ekologicznych inicjatyw.",
                {"satisfaction": 5},
                ["Sfinansować inicjatywy", "Symboliczne wsparcie", "Nie wspierać"],
                {
                    "Sfinansować inicjatywy": {"money": -1000, "satisfaction": 20},
                    "Symboliczne wsparcie": {"money": -200, "satisfaction": 10},
                    "Nie wspierać": {"satisfaction": -10}
                }
            ),
            
            # WYDARZENIA TECHNOLOGICZNE
            Event(
                "Innowacja Technologiczna",
                "Lokalni naukowcy opracowali innowacyjną technologię. Chcą wsparcia na dalsze badania.",
                {"satisfaction": 5},
                ["Sfinansować badania", "Częściowe wsparcie", "Odmówić"],
                {
                    "Sfinansować badania": {"money": -2000, "satisfaction": 15},
                    "Częściowe wsparcie": {"money": -800, "satisfaction": 8},
                    "Odmówić": {"satisfaction": -5}
                }
            ),
            
            # WYDARZENIA SEZONOWE
            Event(
                "Surowa Zima",
                "Nadeszła wyjątkowo surowa zima. Koszty ogrzewania i utrzymania wzrosły.",
                {"money": -1200, "satisfaction": -15},
                ["Zwiększyć pomoc społeczną", "Standardowe działania", "Oszczędzać na wszystkim"],
                {
                    "Zwiększyć pomoc społeczną": {"money": -2000, "satisfaction": 10},
                    "Standardowe działania": {"money": -1200, "satisfaction": -15},
                    "Oszczędzać na wszystkim": {"money": -500, "satisfaction": -30}
                }
            ),
            Event(
                "Fala Upałów",
                "Rekordowe temperatury powodują problemy z dostawami energii i wody.",
                {"money": -800, "satisfaction": -10},
                ["Uruchomić systemy awaryjne", "Racjonować zasoby", "Nic nie robić"],
                {
                    "Uruchomić systemy awaryjne": {"money": -1500, "satisfaction": 5},
                    "Racjonować zasoby": {"money": -400, "satisfaction": -20},
                    "Nic nie robić": {"satisfaction": -25, "population": -20}
                }
            )
        ]
        
        # Statystyki wydarzeń
        self.event_history = []
        self.last_event_turn = 0
        
    def trigger_random_event(self, game_state=None):
        """Wybiera losowe wydarzenie, opcjonalnie uwzględniając stan gry"""
        # Podstawowa implementacja - losowe wydarzenie
        event = random.choice(self.events)
        
        # Można dodać logikę wyboru wydarzenia na podstawie stanu gry
        if game_state:
            event = self._select_contextual_event(game_state)
        
        # Zapisz w historii
        self.event_history.append({
            'event': event,
            'turn': game_state.get('turn', 0) if game_state else 0
        })
        
        return event
    
    def _select_contextual_event(self, game_state):
        """Wybiera wydarzenie na podstawie kontekstu gry"""
        money = game_state.get('money', 0)
        population = game_state.get('population', 0)
        satisfaction = game_state.get('satisfaction', 50)
        
        # Filtruj wydarzenia na podstawie stanu gry
        suitable_events = []
        
        for event in self.events:
            # Logika wyboru wydarzeń na podstawie stanu miasta
            if "Kryzys" in event.title and money < 2000:
                suitable_events.append(event)
            elif "Dotacja" in event.title and satisfaction > 60:
                suitable_events.append(event)
            elif "Protest" in event.title and satisfaction < 40:
                suitable_events.append(event)
            elif "Festiwal" in event.title and money > 5000:
                suitable_events.append(event)
            else:
                # Dodaj wszystkie inne wydarzenia z mniejszym prawdopodobieństwem
                if random.random() < 0.3:
                    suitable_events.append(event)
        
        # Jeśli nie ma odpowiednich wydarzeń, wybierz losowe
        if not suitable_events:
            suitable_events = self.events
        
        return random.choice(suitable_events)
    
    def apply_decision_effects(self, event, decision):
        """Zwraca efekty wybranej decyzji"""
        if decision in event.decision_effects:
            return event.decision_effects[decision]
        else:
            # Jeśli nie ma specjalnych efektów decyzji, zwróć podstawowe efekty
            return event.effects
    
    def get_event_statistics(self):
        """Zwraca statystyki wydarzeń"""
        if not self.event_history:
            return {"total_events": 0, "recent_events": []}
        
        return {
            "total_events": len(self.event_history),
            "recent_events": self.event_history[-5:],  # Ostatnie 5 wydarzeń
            "event_types": self._count_event_types()
        }
    
    def _count_event_types(self):
        """Liczy typy wydarzeń w historii"""
        types = {}
        for entry in self.event_history:
            event_title = entry['event'].title
            if "Pożar" in event_title or "Trzęsienie" in event_title or "Epidemia" in event_title:
                types["Katastrofy"] = types.get("Katastrofy", 0) + 1
            elif "Kryzys" in event_title or "Strajk" in event_title:
                types["Kryzysy"] = types.get("Kryzysy", 0) + 1
            elif "Dotacja" in event_title or "Festiwal" in event_title or "Firma" in event_title:
                types["Pozytywne"] = types.get("Pozytywne", 0) + 1
            elif "Protest" in event_title:
                types["Społeczne"] = types.get("Społeczne", 0) + 1
            else:
                types["Inne"] = types.get("Inne", 0) + 1
        
        return types
