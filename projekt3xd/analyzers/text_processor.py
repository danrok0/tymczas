"""
MODUŁ PRZETWARZANIA TEKSTU - EKSTRAKCJA INFORMACJI Z OPISÓW TRAS
===============================================================

Ten moduł zawiera klasę TextProcessor, która wykorzystuje wyrażenia regularne
do automatycznego wydobywania kluczowych informacji z opisów tras turystycznych.

FUNKCJONALNOŚCI:
- Ekstrakcja czasów przejścia (różne formaty: "2h 30min", "150 minut", "około 4h")
- Rozpoznawanie wysokości i przewyższeń ("1650 m n.p.m.", "przewyższenie 500m")
- Standaryzacja współrzędnych GPS (różne formaty zapisu)
- Identyfikacja punktów charakterystycznych (schroniska, szczyty, przełęcze)
- Rozpoznawanie ostrzeżeń i zagrożeń na trasach
- Określanie poziomu trudności i sezonowości

WYMAGANIA: Implementacja zgodna z specyfikacją z updatelist.txt
AUTOR: System Rekomendacji Tras Turystycznych - Etap 4
"""

# ============================================================================
# IMPORTY BIBLIOTEK
# ============================================================================
import re                                    # Wyrażenia regularne
from typing import Dict, List, Optional, Any, Tuple  # Podpowiedzi typów
from dataclasses import dataclass           # Struktura danych
import logging                              # Logowanie błędów i informacji
import datetime                            # Operacje na datach

# ============================================================================
# KONFIGURACJA LOGOWANIA
# ============================================================================
logging.basicConfig(level=logging.INFO)    # Ustawienia logowania
logger = logging.getLogger(__name__)       # Logger dla tego modułu

# ============================================================================
# STRUKTURY DANYCH
# ============================================================================

@dataclass
class ExtractedTrailInfo:
    """
    Struktura danych przechowująca wszystkie wyekstraktowane informacje o trasie.
    
    Attributes:
        duration_minutes: Czas przejścia w minutach (np. 120 dla 2h)
        elevation_gain: Przewyższenie w metrach (np. 500)
        landmarks: Lista punktów charakterystycznych na trasie
        warnings: Lista ostrzeżeń i zagrożeń
        coordinates: Współrzędne GPS jako tuple (szerokość, długość)
        difficulty_level: Poziom trudności ("łatwa", "średnia", "trudna")
        recommended_season: Zalecana pora roku lub warunki
    
    Wszystkie pola są opcjonalne - jeśli informacja nie została znaleziona,
    pole ma wartość None lub pustą listę.
    """
    duration_minutes: Optional[int] = None              # Czas w minutach
    elevation_gain: Optional[int] = None                # Przewyższenie w metrach
    landmarks: List[str] = None                         # Punkty charakterystyczne
    warnings: List[str] = None                          # Ostrzeżenia
    coordinates: Optional[Tuple[str, str]] = None       # Współrzędne GPS
    difficulty_level: Optional[str] = None              # Poziom trudności
    recommended_season: Optional[str] = None            # Zalecana pora
    
    def __post_init__(self):
        """
        Inicjalizacja pustych list dla pól, które nie mogą być None.
        Wywoływana automatycznie po utworzeniu obiektu.
        """
        if self.landmarks is None:
            self.landmarks = []  # Pusta lista zamiast None
        if self.warnings is None:
            self.warnings = []   # Pusta lista zamiast None

# ============================================================================
# GŁÓWNA KLASA PROCESORA TEKSTU
# ============================================================================

class TextProcessor:
    """
    Główna klasa do przetwarzania tekstów opisów tras i ekstrakcji informacji
    używając zaawansowanych wyrażeń regularnych.
    
    Klasa implementuje kompleksowy system rozpoznawania wzorców w tekstach
    polskojęzycznych opisów tras turystycznych. Wykorzystuje predefiniowane
    wzorce regex do identyfikacji różnych typów informacji.
    
    Przykład użycia:
        processor = TextProcessor()
        info = processor.process_trail_description("Trasa 5km, 2h 30min, 
                                                    przełęcz Zawrat 2159m n.p.m.")
        print(f"Czas: {info.duration_minutes} minut")
    """
    
    def __init__(self):
        """
        Inicjalizacja wszystkich wzorców wyrażeń regularnych.
        
        Tworzy słownik wzorców regex podzielonych na kategorie:
        - duration: różne formaty czasu przejścia
        - elevation: wysokości i przewyższenia  
        - coordinates: współrzędne GPS w różnych formatach
        - landmarks: punkty charakterystyczne
        - warnings: ostrzeżenia i zagrożenia
        - difficulty: poziomy trudności
        - season: informacje o sezonowości
        """
        # ====================================================================
        # WZORCE WYRAŻEŃ REGULARNYCH - zgodnie z wymaganiami updatelist.txt
        # ====================================================================
        self.patterns = {
            # Czas przejścia: r'(\d+(?:\.\d+)?)\s*(?:h|godz|hours?)|(\d+)\s*(?:min|minut)'
            'duration': [
                re.compile(r'(\d+(?:\.\d+)?)\s*(?:h|godz|godzin|hours?)', re.IGNORECASE),
                re.compile(r'(\d+)\s*(?:min|minut)', re.IGNORECASE),
                re.compile(r'(\d+)\s*h\s*(\d+)\s*min', re.IGNORECASE),
                re.compile(r'około\s*(\d+(?:\.\d+)?)\s*(?:h|godz|godzin)', re.IGNORECASE),
                re.compile(r'(\d+)-(\d+)\s*(?:h|godz|godzin)', re.IGNORECASE)
            ],
            
            # Wysokości: r'(\d{3,4})\s*m\s*n\.p\.m\.'
            'elevation': [
                re.compile(r'(\d{3,4})\s*m\s*n\.?p\.?m\.?', re.IGNORECASE),
                re.compile(r'przewyższenie[:\s]*(\d{3,4})\s*m', re.IGNORECASE),
                re.compile(r'wysokość[:\s]*(\d{3,4})\s*m', re.IGNORECASE)
            ],
            
            # Współrzędne GPS: r'([NS]?\d{1,2}[°º]\d{1,2}[\'′]\d{1,2}[\"″]?)\s*,?\s*([EW]?\d{1,3}[°º]\d{1,2}[\'′]\d{1,2}[\"″]?)'
            'coordinates': [
                re.compile(r'([NS]?\d{1,2}[°º]\d{1,2}[\'′]\d{1,2}[\"″]?)\s*,?\s*([EW]?\d{1,3}[°º]\d{1,2}[\'′]\d{1,2}[\"″]?)', re.IGNORECASE),
                re.compile(r'(\d{2}\.\d{4,})[°\s]*N[,\s]*(\d{2}\.\d{4,})[°\s]*E', re.IGNORECASE),
                re.compile(r'N\s*(\d{2}[°º]\d{2}[\'′]\d{2}[\"″]?)\s*E\s*(\d{2}[°º]\d{2}[\'′]\d{2}[\"″]?)', re.IGNORECASE)
            ],
            
            # Punkty charakterystyczne
            'landmarks': [
                re.compile(r'(schronisko\s+\w+)', re.IGNORECASE),
                re.compile(r'(szczyt\s+\w+)', re.IGNORECASE),
                re.compile(r'(przełęcz\s+\w+)', re.IGNORECASE),
                re.compile(r'(dolina\s+\w+)', re.IGNORECASE),
                re.compile(r'(jezioro\s+\w+)', re.IGNORECASE),
                re.compile(r'(wodospad\s+\w+)', re.IGNORECASE),
                re.compile(r'(punkt\s+widokowy)', re.IGNORECASE)
            ],
            
            # Ostrzeżenia i zagrożenia
            'warnings': [
                re.compile(r'uwaga[:\s]*([\w\s,]+(?:po\s+deszczu|śliskie|niebezpieczne|trudne|strome)[\w\s]*)', re.IGNORECASE),
                re.compile(r'((?:śliskie|niebezpieczne|trudne|strome)[\w\s]*)', re.IGNORECASE),
                re.compile(r'ostrzeżenie[:\s]*([\w\s,]+)', re.IGNORECASE),
                re.compile(r'(zagrożenie[\w\s]*)', re.IGNORECASE)
            ],
            
            # Poziom trudności
            'difficulty': [
                re.compile(r'trasa\s+(łatwa|średnia|średnio\s+trudna|trudna|bardzo\s+trudna)', re.IGNORECASE),
                re.compile(r'poziom\s+trudności[:\s]*(łatwy|średni|trudny)', re.IGNORECASE),
                re.compile(r'(łatwa|średnia|trudna)\s+trasa', re.IGNORECASE)
            ],
            
            # Sezonowość i zalecane pory
            'season': [
                re.compile(r'najlepiej\s+(wiosną|latem|jesienią|zimą)', re.IGNORECASE),
                re.compile(r'zalecana\s+pora[:\s]*([\w\s]+)', re.IGNORECASE),
                re.compile(r'(wczesnym\s+rankiem|wieczorem|w\s+południe)', re.IGNORECASE),
                re.compile(r'sezon[:\s]*([\w\s-]+)', re.IGNORECASE)
            ]
        }
    
    def extract_duration(self, text: str) -> Optional[int]:
        """
        Wydobywa czas przejścia w różnych formatach i konwertuje na minuty.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Czas w minutach lub None jeśli nie znaleziono
        """
        for pattern in self.patterns['duration']:
            matches = pattern.findall(text)
            if matches:
                try:
                    match = matches[0]
                    if isinstance(match, tuple):
                        if len(match) == 2 and match[0] and match[1]:
                            # Format "X h Y min"
                            hours = float(match[0])
                            minutes = float(match[1])
                            return int(hours * 60 + minutes)
                        elif len(match) == 2 and match[0] and not match[1]:
                            # Tylko godziny
                            return int(float(match[0]) * 60)
                        elif len(match) == 2 and not match[0] and match[1]:
                            # Tylko minuty
                            return int(float(match[1]))
                    else:
                        # Pojedyncza wartość
                        if 'min' in text.lower():
                            return int(float(match))
                        else:
                            return int(float(match) * 60)
                except (ValueError, TypeError):
                    continue
        return None
    
    def extract_elevation(self, text: str) -> Optional[int]:
        """
        Wydobywa informacje o wysokości/przewyższeniu.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Wysokość w metrach lub None jeśli nie znaleziono
        """
        for pattern in self.patterns['elevation']:
            matches = pattern.findall(text)
            if matches:
                try:
                    return int(matches[0])
                except (ValueError, TypeError):
                    continue
        return None
    
    def extract_coordinates(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Standaryzuje różne formaty zapisu współrzędnych geograficznych.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Tuple (latitude, longitude) lub None jeśli nie znaleziono
        """
        for pattern in self.patterns['coordinates']:
            matches = pattern.findall(text)
            if matches:
                try:
                    match = matches[0]
                    if isinstance(match, tuple) and len(match) == 2:
                        return (match[0].strip(), match[1].strip())
                except (ValueError, TypeError):
                    continue
        return None
    
    def extract_landmarks(self, text: str) -> List[str]:
        """
        Identyfikuje punkty charakterystyczne na trasie.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Lista znalezionych punktów charakterystycznych
        """
        landmarks = []
        for pattern in self.patterns['landmarks']:
            matches = pattern.findall(text)
            landmarks.extend([match.strip() for match in matches])
        
        # Usuwanie duplikatów z zachowaniem kolejności
        return list(dict.fromkeys(landmarks))
    
    def extract_warnings(self, text: str) -> List[str]:
        """
        Rozpoznaje ostrzeżenia i zagrożenia w opisach tras.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Lista znalezionych ostrzeżeń
        """
        warnings = []
        for pattern in self.patterns['warnings']:
            matches = pattern.findall(text)
            warnings.extend([match.strip() for match in matches if match.strip()])
        
        # Usuwanie duplikatów z zachowaniem kolejności
        return list(dict.fromkeys(warnings))
    
    def extract_difficulty(self, text: str) -> Optional[str]:
        """
        Ekstraktuje poziom trudności trasy.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Poziom trudności lub None jeśli nie znaleziono
        """
        for pattern in self.patterns['difficulty']:
            matches = pattern.findall(text)
            if matches:
                return matches[0].strip().lower()
        return None
    
    def extract_season_info(self, text: str) -> Optional[str]:
        """
        Wydobywa informacje o sezonowości i zalecanych porach.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Informacje o sezonowości lub None jeśli nie znaleziono
        """
        for pattern in self.patterns['season']:
            matches = pattern.findall(text)
            if matches:
                return matches[0].strip()
        return None
    
    def process_trail_description(self, description: str) -> ExtractedTrailInfo:
        """
        Główna metoda przetwarzająca opis trasy i ekstraktująca wszystkie informacje.
        
        Args:
            description: Pełny opis trasy do analizy
            
        Returns:
            ExtractedTrailInfo z wyekstraktowanymi danymi
        """
        if not description or not isinstance(description, str):
            return ExtractedTrailInfo()
        
        logger.info(f"Przetwarzanie opisu trasy: {description[:100]}...")
        
        extracted_info = ExtractedTrailInfo(
            duration_minutes=self.extract_duration(description),
            elevation_gain=self.extract_elevation(description),
            landmarks=self.extract_landmarks(description),
            warnings=self.extract_warnings(description),
            coordinates=self.extract_coordinates(description),
            difficulty_level=self.extract_difficulty(description),
            recommended_season=self.extract_season_info(description)
        )
        
        logger.info(f"Wyekstraktowano: czas={extracted_info.duration_minutes}min, "
                   f"przewyższenie={extracted_info.elevation_gain}m, "
                   f"punkty={len(extracted_info.landmarks)}, "
                   f"ostrzeżenia={len(extracted_info.warnings)}")
        
        return extracted_info
    
    def enhance_trail_data(self, trail_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rozszerza dane trasy o informacje wyekstraktowane z opisu.
        
        Args:
            trail_data: Słownik z danymi trasy
            
        Returns:
            Rozszerzony słownik z dodatkowymi informacjami
        """
        enhanced_trail = trail_data.copy()
        
        # Pobierz opis trasy
        description = trail_data.get('description', '')
        if not description:
            return enhanced_trail
        
        # Przetwórz opis
        extracted_info = self.process_trail_description(description)
        
        # Dodaj wyekstraktowane informacje do danych trasy
        enhanced_trail.update({
            'extracted_duration_minutes': extracted_info.duration_minutes,
            'extracted_elevation_gain': extracted_info.elevation_gain,
            'landmarks': extracted_info.landmarks,
            'warnings': extracted_info.warnings,
            'extracted_coordinates': extracted_info.coordinates,
            'extracted_difficulty': extracted_info.difficulty_level,
            'recommended_season': extracted_info.recommended_season,
            'processing_timestamp': datetime.datetime.now().isoformat()
        })
        
        return enhanced_trail