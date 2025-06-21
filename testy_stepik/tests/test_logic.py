import unittest
import tempfile
import os
import sys
import csv

# Dodaj główny katalog do ścieżki Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_handling import FileRouteRepository
from logic import RouteRecommender
from models import UserPreference, Route


class TestRouteRecommender(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie tymczasowych plików i danych testowych"""
        # Tworzymy tymczasowy katalog
        self.temp_dir = tempfile.mkdtemp()
        
        # Ścieżka do pliku testowego
        self.test_file_path = os.path.join(self.temp_dir, "integration_test_routes.csv")
        
        # Dane testowe z różnymi trasami
        self.test_routes_data = [
            {'name': 'Easy Park Walk', 'distance': '3.0', 'difficulty': '1', 'terrain': 'park'},
            {'name': 'Forest Trail', 'distance': '8.5', 'difficulty': '2', 'terrain': 'forest'},
            {'name': 'Mountain Hike', 'distance': '15.0', 'difficulty': '4', 'terrain': 'mountain'},
            {'name': 'Desert Adventure', 'distance': '22.0', 'difficulty': '5', 'terrain': 'desert'},
            {'name': 'City Stroll', 'distance': '4.2', 'difficulty': '1', 'terrain': 'urban'},
            {'name': 'Coastal Path', 'distance': '12.3', 'difficulty': '3', 'terrain': 'coastal'},
            {'name': 'Extreme Mountain', 'distance': '30.0', 'difficulty': '5', 'terrain': 'mountain'},
            {'name': 'Easy Forest', 'distance': '5.0', 'difficulty': '2', 'terrain': 'forest'},
            {'name': 'Urban Challenge', 'distance': '18.0', 'difficulty': '4', 'terrain': 'urban'}
        ]
        
        # Tworzenie pliku CSV z danymi testowymi
        self._create_csv_file(self.test_file_path, self.test_routes_data)
        
        # Tworzenie repository i recommendera
        self.repository = FileRouteRepository(self.test_file_path)
        self.recommender = RouteRecommender(self.repository)
    
    def tearDown(self):
        """Czyszczenie tymczasowych plików po testach"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_csv_file(self, file_path, routes_data):
        """Pomocnicza metoda do tworzenia pliku CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for route_data in routes_data:
                writer.writerow(route_data)
    
    def test_recommend_filter_by_max_difficulty(self):
        """Test filtrowania tras według maksymalnej trudności"""
        # Preferencje: maksymalna trudność 2
        preference = UserPreference(max_difficulty=2)
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Sprawdzenie, że wszystkie zwrócone trasy mają trudność <= 2
        self.assertTrue(len(recommended_routes) > 0)
        for route in recommended_routes:
            self.assertLessEqual(route.difficulty, 2)
        
        # Sprawdzenie konkretnych tras, które powinny być zwrócone
        route_names = [route.name for route in recommended_routes]
        expected_routes = ['Easy Park Walk', 'Forest Trail', 'City Stroll', 'Easy Forest']
        
        self.assertEqual(len(recommended_routes), 4)
        for expected_name in expected_routes:
            self.assertIn(expected_name, route_names)
    
    def test_recommend_filter_by_terrain(self):
        """Test filtrowania tras według typu terenu"""
        # Preferencje: teren górski
        preference = UserPreference(terrain='mountain')
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Sprawdzenie, że wszystkie zwrócone trasy są górskie
        self.assertTrue(len(recommended_routes) > 0)
        for route in recommended_routes:
            self.assertEqual(route.terrain, 'mountain')
        
        # Sprawdzenie konkretnych tras
        route_names = [route.name for route in recommended_routes]
        expected_routes = ['Mountain Hike', 'Extreme Mountain']
        
        self.assertEqual(len(recommended_routes), 2)
        for expected_name in expected_routes:
            self.assertIn(expected_name, route_names)
    
    def test_recommend_filter_by_max_distance(self):
        """Test filtrowania tras według maksymalnego dystansu"""
        # Preferencje: maksymalny dystans 10 km
        preference = UserPreference(max_distance=10.0)
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Sprawdzenie, że wszystkie zwrócone trasy mają dystans <= 10.0
        self.assertTrue(len(recommended_routes) > 0)
        for route in recommended_routes:
            self.assertLessEqual(route.distance, 10.0)
        
        # Sprawdzenie konkretnych tras
        route_names = [route.name for route in recommended_routes]
        expected_routes = ['Easy Park Walk', 'Forest Trail', 'City Stroll', 'Easy Forest']
        
        self.assertEqual(len(recommended_routes), 4)
        for expected_name in expected_routes:
            self.assertIn(expected_name, route_names)
    
    def test_recommend_combined_filters(self):
        """Test filtrowania tras z kombinacją kryteriów"""
        # Preferencje: maksymalna trudność 3, teren leśny, maksymalny dystans 10 km
        preference = UserPreference(max_difficulty=3, terrain='forest', max_distance=10.0)
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Sprawdzenie wszystkich kryteriów
        for route in recommended_routes:
            self.assertLessEqual(route.difficulty, 3)
            self.assertEqual(route.terrain, 'forest')
            self.assertLessEqual(route.distance, 10.0)
        
        # Sprawdzenie konkretnych tras - powinny być 'Forest Trail' i 'Easy Forest'
        self.assertEqual(len(recommended_routes), 2)
        route_names = [route.name for route in recommended_routes]
        expected_routes = ['Forest Trail', 'Easy Forest']
        for expected_name in expected_routes:
            self.assertIn(expected_name, route_names)
    
    def test_recommend_strict_difficulty_and_terrain(self):
        """Test poprawnego filtrowania z trudnością i terenem"""
        # Preferencje: maksymalna trudność 3, teren górski
        preference = UserPreference(max_difficulty=3, terrain='mountain')
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Powinien być tylko 'Mountain Hike' (trudność 4 > 3, więc 'Extreme Mountain' wykluczone)
        # Właściwie nie, 'Mountain Hike' ma trudność 4, więc też powinien być wykluczone
        # Sprawdźmy dane testowe ponownie...
        # 'Mountain Hike' ma trudność 4, 'Extreme Mountain' ma trudność 5
        # Więc żadna z tras górskich nie spełnia kryterium max_difficulty=3
        
        self.assertEqual(len(recommended_routes), 0)
    
    def test_recommend_no_matching_routes_difficulty(self):
        """Test braku pasujących tras - zbyt niska trudność"""
        # Preferencje: maksymalna trudność 0 (niemożliwe, bo minimalna to 1)
        # Ale sprawdźmy z bardzo restrykcyjnymi kryteriami
        preference = UserPreference(max_difficulty=1, terrain='mountain')
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Nie ma tras górskich o trudności 1
        self.assertEqual(recommended_routes, [])
        self.assertIsInstance(recommended_routes, list)
    
    def test_recommend_no_matching_routes_terrain(self):
        """Test braku pasujących tras - nieistniejący typ terenu"""
        # Preferencje: teren, którego nie ma w danych
        preference = UserPreference(terrain='underwater')
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Nie ma tras podwodnych
        self.assertEqual(recommended_routes, [])
        self.assertIsInstance(recommended_routes, list)
    
    def test_recommend_no_matching_routes_distance(self):
        """Test braku pasujących tras - zbyt mały maksymalny dystans"""
        # Preferencje: maksymalny dystans 1 km (mniejszy niż wszystkie trasy)
        preference = UserPreference(max_distance=1.0)
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Nie ma tras krótszych niż 1 km
        self.assertEqual(recommended_routes, [])
        self.assertIsInstance(recommended_routes, list)
    
    def test_recommend_all_routes_no_preferences(self):
        """Test zwracania wszystkich tras przy braku ograniczeń"""
        # Preferencje: brak ograniczeń
        preference = UserPreference()
        
        recommended_routes = self.recommender.recommend(preference)
        
        # Powinny być zwrócone wszystkie trasy
        self.assertEqual(len(recommended_routes), 9)  # Wszystkie trasy z danych testowych
        
        # Sprawdzenie, że zwrócone są obiekty Route
        for route in recommended_routes:
            self.assertIsInstance(route, Route)
    
    def test_recommend_boundary_values(self):
        """Test wartości granicznych"""
        # Test z maksymalną możliwą trudnością
        preference = UserPreference(max_difficulty=5)
        recommended_routes = self.recommender.recommend(preference)
        self.assertEqual(len(recommended_routes), 9)  # Wszystkie trasy
        
        # Test z minimalną możliwą trudnością
        preference = UserPreference(max_difficulty=1)
        recommended_routes = self.recommender.recommend(preference)
        easy_routes = [route for route in recommended_routes if route.difficulty == 1]
        self.assertEqual(len(easy_routes), len(recommended_routes))  # Tylko trasy o trudności 1
    
    def test_recommend_single_criterion_each(self):
        """Test każdego kryterium osobno"""
        # Tylko trudność
        preference = UserPreference(max_difficulty=3)
        routes = self.recommender.recommend(preference)
        for route in routes:
            self.assertLessEqual(route.difficulty, 3)
        
        # Tylko teren
        preference = UserPreference(terrain='urban')
        routes = self.recommender.recommend(preference)
        for route in routes:
            self.assertEqual(route.terrain, 'urban')
        expected_urban = ['City Stroll', 'Urban Challenge']
        route_names = [route.name for route in routes]
        for expected in expected_urban:
            self.assertIn(expected, route_names)
        
        # Tylko dystans
        preference = UserPreference(max_distance=15.0)
        routes = self.recommender.recommend(preference)
        for route in routes:
            self.assertLessEqual(route.distance, 15.0)
    
    def test_recommend_invalid_user_preference(self):
        """Test z nieprawidłowym obiektem preferencji"""
        with self.assertRaises(ValueError) as context:
            self.recommender.recommend("not a preference")
        
        self.assertIn("user_preference must be an instance of UserPreference", str(context.exception))
    
    def test_repository_integration(self):
        """Test integracji z repository"""
        # Test, że recommender rzeczywiście używa repository
        self.assertIsInstance(self.recommender.repository, FileRouteRepository)
        self.assertEqual(self.recommender.repository.file_path, self.test_file_path)
        
        # Test, że mogę pobrać wszystkie trasy przez repository
        all_routes = self.repository.get_all()
        self.assertEqual(len(all_routes), 9)
    
    def test_recommend_with_empty_repository(self):
        """Test z pustym repository"""
        # Tworzenie pustego pliku CSV
        empty_file_path = os.path.join(self.temp_dir, "empty.csv")
        with open(empty_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        
        empty_repository = FileRouteRepository(empty_file_path)
        empty_recommender = RouteRecommender(empty_repository)
        
        preference = UserPreference(max_difficulty=3)
        recommended_routes = empty_recommender.recommend(preference)
        
        self.assertEqual(recommended_routes, [])


if __name__ == '__main__':
    unittest.main() 