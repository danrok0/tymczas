#!/usr/bin/env python3
"""
Demonstracja systemu rekomendacji tras.

Ten skrypt pokazuje, jak używać systemu do zarządzania trasami i rekomendacji.
"""

import csv
import os
from models import Route, UserPreference
from data_handling import FileRouteRepository, DataParsingError
from logic import RouteRecommender


def create_sample_data_file(filename="sample_routes.csv"):
    """Tworzy przykładowy plik z danymi tras"""
    sample_routes = [
        {'name': 'Łatwy spacer po parku', 'distance': '3.5', 'difficulty': '1', 'terrain': 'park'},
        {'name': 'Leśna ścieżka', 'distance': '7.2', 'difficulty': '2', 'terrain': 'forest'},
        {'name': 'Górski szlak', 'distance': '12.8', 'difficulty': '4', 'terrain': 'mountain'},
        {'name': 'Spacer po mieście', 'distance': '5.0', 'difficulty': '1', 'terrain': 'urban'},
        {'name': 'Nadbrzeżna trasa', 'distance': '9.3', 'difficulty': '3', 'terrain': 'coastal'},
        {'name': 'Pustynia - wyzwanie', 'distance': '20.0', 'difficulty': '5', 'terrain': 'desert'},
        {'name': 'Łagodny las', 'distance': '6.5', 'difficulty': '2', 'terrain': 'forest'},
        {'name': 'Ekstremalna góra', 'distance': '25.0', 'difficulty': '5', 'terrain': 'mountain'},
        {'name': 'Rowerówka miejska', 'distance': '8.0', 'difficulty': '2', 'terrain': 'urban'},
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['name', 'distance', 'difficulty', 'terrain']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for route in sample_routes:
            writer.writerow(route)
    
    print(f"✓ Utworzono plik z przykładowymi danymi: {filename}")


def demonstrate_models():
    """Demonstracja tworzenia obiektów Route i UserPreference"""
    print("\n" + "="*50)
    print("DEMONSTRACJA MODELI")
    print("="*50)
    
    # Tworzenie obiektów Route
    print("\n1. Tworzenie tras:")
    try:
        route1 = Route("Górski szlak", 15.5, 4, "mountain")
        route2 = Route("Spacer po parku", 3.0, 1, "park")
        print(f"   ✓ {route1}")
        print(f"   ✓ {route2}")
    except ValueError as e:
        print(f"   ✗ Błąd: {e}")
    
    # Testowanie walidacji
    print("\n2. Testowanie walidacji Route:")
    try:
        invalid_route = Route("Błędna trasa", -5.0, 2, "forest")
    except ValueError as e:
        print(f"   ✓ Poprawnie wykryto błąd: {e}")
    
    # Tworzenie preferencji użytkownika
    print("\n3. Tworzenie preferencji użytkownika:")
    pref1 = UserPreference(max_difficulty=3, terrain="forest")
    pref2 = UserPreference(max_distance=10.0)
    pref3 = UserPreference()  # Brak ograniczeń
    
    print(f"   ✓ {pref1}")
    print(f"   ✓ {pref2}")
    print(f"   ✓ {pref3}")


def demonstrate_data_handling(filename="sample_routes.csv"):
    """Demonstracja obsługi danych z pliku CSV"""
    print("\n" + "="*50)
    print("DEMONSTRACJA OBSŁUGI DANYCH")
    print("="*50)
    
    try:
        # Tworzenie repository
        repository = FileRouteRepository(filename)
        print(f"\n1. Utworzono FileRouteRepository dla pliku: {filename}")
        
        # Wczytywanie tras
        routes = repository.get_all()
        print(f"   ✓ Wczytano {len(routes)} tras z pliku")
        
        # Wyświetlenie pierwszych kilku tras
        print("\n2. Przykładowe trasy:")
        for i, route in enumerate(routes[:3]):
            print(f"   {i+1}. {route}")
        
        if len(routes) > 3:
            print(f"   ... i {len(routes)-3} więcej")
            
    except FileNotFoundError:
        print(f"   ✗ Nie znaleziono pliku: {filename}")
    except DataParsingError as e:
        print(f"   ✗ Błąd parsowania danych: {e}")


def demonstrate_recommendations(filename="sample_routes.csv"):
    """Demonstracja systemu rekomendacji"""
    print("\n" + "="*50)
    print("DEMONSTRACJA SYSTEMU REKOMENDACJI")
    print("="*50)
    
    try:
        # Tworzenie systemu rekomendacji
        repository = FileRouteRepository(filename)
        recommender = RouteRecommender(repository)
        
        print("\n1. Utworzono system rekomendacji")
        
        # Scenariusz 1: Łatwe trasy
        print("\n2. Scenariusz: Szukam łatwych tras (max trudność: 2)")
        preference = UserPreference(max_difficulty=2)
        recommended = recommender.recommend(preference)
        
        print(f"   Znaleziono {len(recommended)} tras:")
        for route in recommended:
            print(f"   - {route.name} (trudność: {route.difficulty}, dystans: {route.distance}km)")
        
        # Scenariusz 2: Trasy leśne
        print("\n3. Scenariusz: Szukam tras leśnych")
        preference = UserPreference(terrain="forest")
        recommended = recommender.recommend(preference)
        
        print(f"   Znaleziono {len(recommended)} tras:")
        for route in recommended:
            print(f"   - {route.name} (teren: {route.terrain}, dystans: {route.distance}km)")
        
        # Scenariusz 3: Kombinacja kryteriów
        print("\n4. Scenariusz: Krótkie i łatwe trasy (max 8km, max trudność 2)")
        preference = UserPreference(max_distance=8.0, max_difficulty=2)
        recommended = recommender.recommend(preference)
        
        print(f"   Znaleziono {len(recommended)} tras:")
        for route in recommended:
            print(f"   - {route.name} (trudność: {route.difficulty}, dystans: {route.distance}km)")
        
        # Scenariusz 4: Brak pasujących tras
        print("\n5. Scenariusz: Bardzo restrykcyjne kryteria (podwodne trasy)")
        preference = UserPreference(terrain="underwater")
        recommended = recommender.recommend(preference)
        
        if recommended:
            print(f"   Znaleziono {len(recommended)} tras")
        else:
            print("   Nie znaleziono pasujących tras ❌")
            
    except Exception as e:
        print(f"   ✗ Błąd: {e}")


def cleanup(filename="sample_routes.csv"):
    """Czyszczenie plików demonstracyjnych"""
    if os.path.exists(filename):
        os.remove(filename)
        print(f"\n✓ Usunięto plik demonstracyjny: {filename}")


def main():
    """Główna funkcja demonstracyjna"""
    print("DEMONSTRACJA SYSTEMU REKOMENDACJI TRAS")
    print("=" * 70)
    
    filename = "sample_routes.csv"
    
    try:
        # 1. Tworzenie przykładowych danych
        create_sample_data_file(filename)
        
        # 2. Demonstracja modeli
        demonstrate_models()
        
        # 3. Demonstracja obsługi danych
        demonstrate_data_handling(filename)
        
        # 4. Demonstracja rekomendacji
        demonstrate_recommendations(filename)
        
        print("\n" + "="*70)
        print("DEMONSTRACJA ZAKOŃCZONA POMYŚLNIE ✓")
        print("="*70)
        
        # Opcjonalne czyszczenie
        response = input("\nCzy usunąć plik demonstracyjny? (t/n): ").lower().strip()
        if response in ['t', 'tak', 'y', 'yes']:
            cleanup(filename)
        
    except Exception as e:
        print(f"\n✗ Wystąpił błąd podczas demonstracji: {e}")
        cleanup(filename)


if __name__ == '__main__':
    main() 