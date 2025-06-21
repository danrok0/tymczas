#!/usr/bin/env python3
"""
Szybki test systemu - sprawdza czy wszystko działa poprawnie
"""

import sys
import os
import time

def quick_test():
    """Szybki test funkcjonalności"""
    print("SZYBKI TEST SYSTEMU")
    print("="*50)
    
    try:
        # Test 1: Import modułów
        print("1. Import modułów...", end=" ")
        from models import Route, UserPreference
        from data_handling import FileRouteRepository, DataParsingError
        from logic import RouteRecommender
        print("✅")
        
        # Test 2: Tworzenie obiektów
        print("2. Tworzenie obiektów...", end=" ")
        route = Route("Testowa trasa", 12.5, 3, "mountain")
        preference = UserPreference(max_difficulty=4, terrain="mountain")
        print("✅")
        
        # Test 3: Walidacja
        print("3. Walidacja danych...", end=" ")
        try:
            invalid_route = Route("", -1, 0, "")
            print("❌ (walidacja nie działa)")
            return False
        except ValueError:
            print("✅")
        
        # Test 4: Tymczasowy plik CSV
        print("4. Obsługa plików CSV...", end=" ")
        import tempfile
        import csv
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'distance', 'difficulty', 'terrain'])
            writer.writeheader()
            writer.writerow({'name': 'Test', 'distance': '10', 'difficulty': '2', 'terrain': 'forest'})
            temp_file = f.name
        
        try:
            repository = FileRouteRepository(temp_file)
            routes = repository.get_all()
            if len(routes) == 1:
                print("✅")
            else:
                print(f"❌ (oczekiwano 1 trasę, otrzymano {len(routes)})")
                return False
        finally:
            os.unlink(temp_file)
        
        # Test 5: System rekomendacji
        print("5. System rekomendacji...", end=" ")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'distance', 'difficulty', 'terrain'])
            writer.writeheader()
            writer.writerow({'name': 'Easy', 'distance': '5', 'difficulty': '1', 'terrain': 'park'})
            writer.writerow({'name': 'Hard', 'distance': '20', 'difficulty': '5', 'terrain': 'mountain'})
            temp_file = f.name
        
        try:
            repository = FileRouteRepository(temp_file)
            recommender = RouteRecommender(repository)
            
            # Filtruj tylko łatwe trasy
            easy_pref = UserPreference(max_difficulty=2)
            easy_routes = recommender.recommend(easy_pref)
            
            if len(easy_routes) == 1 and easy_routes[0].name == 'Easy':
                print("✅")
            else:
                print(f"❌ (błąd filtrowania)")
                return False
        finally:
            os.unlink(temp_file)
        
        print("\n🎉 WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE!")
        return True
        
    except ImportError as e:
        print(f"❌ Błąd importu: {e}")
        return False
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return False


def run_unit_tests():
    """Uruchom pełny zestaw testów jednostkowych"""
    print("\nUruchamianie pełnych testów...")
    print("-" * 50)
    
    import subprocess
    try:
        result = subprocess.run([sys.executable, 'run_tests.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Pełne testy: SUKCES")
            # Policz liczbę testów
            lines = result.stderr.split('\n')
            for line in lines:
                if 'Ran' in line and 'tests' in line:
                    print(f"   {line}")
            return True
        else:
            print("❌ Pełne testy: BŁĄD")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Testy przekroczyły limit czasu")
        return False
    except Exception as e:
        print(f"❌ Błąd podczas testów: {e}")
        return False


def main():
    """Główna funkcja"""
    start_time = time.time()
    
    # Szybki test
    if not quick_test():
        print("\n❌ SZYBKI TEST NIEUDANY!")
        return 1
    
    # Pełne testy (opcjonalnie)
    response = input("\nCzy uruchomić pełny zestaw testów? (t/n): ").lower().strip()
    if response in ['t', 'tak', 'y', 'yes']:
        if not run_unit_tests():
            print("\n❌ PEŁNE TESTY NIEUDANE!")
            return 1
    
    # Podsumowanie
    elapsed = time.time() - start_time
    print(f"\n✅ SYSTEM DZIAŁA POPRAWNIE!")
    print(f"⏱️  Czas wykonania: {elapsed:.2f}s")
    print("\nGotowe do użycia:")
    print("  python demo.py      - demonstracja")
    print("  python run_tests.py - wszystkie testy")
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 