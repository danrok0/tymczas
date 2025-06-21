#!/usr/bin/env python3
"""
Skrypt do uruchamiania wszystkich testów dla systemu rekomendacji tras.

Uruchamia wszystkie testy z pakietu tests/:
- test_models.py - testy modeli Route i UserPreference
- test_data_handling.py - testy obsługi danych i FileRouteRepository
- test_logic.py - testy integracyjne RouteRecommender

Użycie:
    python run_tests.py
    lub
    python -m unittest discover tests
"""

import unittest
import sys
import os

# Dodaj główny katalog do ścieżki Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_all_tests():
    """Uruchamia wszystkie testy z pakietu tests"""
    # Znajdź wszystkie testy w katalogu tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)
    
    # Uruchom testy z szczegółowym raportowaniem
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zwróć kod wyjścia (0 = sukces, 1 = błędy)
    return 0 if result.wasSuccessful() else 1


def run_specific_test_module(module_name):
    """Uruchamia testy z konkretnego modułu"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{module_name}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Uruchom konkretny moduł testowy
        module_to_test = sys.argv[1]
        print(f"Uruchamianie testów z modułu: {module_to_test}")
        exit_code = run_specific_test_module(module_to_test)
    else:
        # Uruchom wszystkie testy
        print("Uruchamianie wszystkich testów...")
        print("=" * 70)
        exit_code = run_all_tests()
    
    sys.exit(exit_code) 