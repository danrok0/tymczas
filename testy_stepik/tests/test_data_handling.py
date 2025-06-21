import unittest
import tempfile
import os
import sys
import csv

# Dodaj główny katalog do ścieżki Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_handling import FileRouteRepository, DataParsingError
from models import Route


class TestFileRouteRepository(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie tymczasowych plików na potrzeby testów"""
        # Tworzymy tymczasowy katalog
        self.temp_dir = tempfile.mkdtemp()
        
        # Ścieżka do pliku testowego
        self.test_file_path = os.path.join(self.temp_dir, "test_routes.csv")
        
        # Ścieżka do pliku z błędnymi danymi
        self.error_file_path = os.path.join(self.temp_dir, "error_routes.csv")
        
        # Ścieżka do pustego pliku
        self.empty_file_path = os.path.join(self.temp_dir, "empty_routes.csv")
        
        # Ścieżka do nieistniejącego pliku
        self.nonexistent_file_path = os.path.join(self.temp_dir, "nonexistent.csv")
    
    def tearDown(self):
        """Czyszczenie tymczasowych plików po testach"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_valid_csv_file(self, file_path, routes_data):
        """Pomocnicza metoda do tworzenia poprawnego pliku CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for route_data in routes_data:
                writer.writerow(route_data)
    
    def test_get_all_valid_data(self):
        """Test scenariusza idealnego - poprawne dane CSV"""
        # Przygotowanie danych testowych
        test_data = [
            {'name': 'Mountain Trail', 'distance': '15.5', 'difficulty': '3', 'terrain': 'mountain'},
            {'name': 'Forest Path', 'distance': '8.0', 'difficulty': '2', 'terrain': 'forest'},
            {'name': 'City Walk', 'distance': '5.2', 'difficulty': '1', 'terrain': 'urban'},
            {'name': 'Desert Route', 'distance': '25.0', 'difficulty': '5', 'terrain': 'desert'}
        ]
        
        self._create_valid_csv_file(self.test_file_path, test_data)
        
        # Test
        repository = FileRouteRepository(self.test_file_path)
        routes = repository.get_all()
        
        # Sprawdzenia
        self.assertEqual(len(routes), 4)
        
        # Sprawdzenie pierwszej trasy
        self.assertIsInstance(routes[0], Route)
        self.assertEqual(routes[0].name, 'Mountain Trail')
        self.assertEqual(routes[0].distance, 15.5)
        self.assertEqual(routes[0].difficulty, 3)
        self.assertEqual(routes[0].terrain, 'mountain')
        
        # Sprawdzenie ostatniej trasy
        self.assertEqual(routes[3].name, 'Desert Route')
        self.assertEqual(routes[3].distance, 25.0)
        self.assertEqual(routes[3].difficulty, 5)
        self.assertEqual(routes[3].terrain, 'desert')
    
    def test_get_all_with_integer_distance(self):
        """Test obsługi dystansu jako liczby całkowitej"""
        test_data = [
            {'name': 'Short Trail', 'distance': '10', 'difficulty': '2', 'terrain': 'park'}
        ]
        
        self._create_valid_csv_file(self.test_file_path, test_data)
        
        repository = FileRouteRepository(self.test_file_path)
        routes = repository.get_all()
        
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].distance, 10.0)
    
    def test_get_all_data_parsing_error_invalid_difficulty(self):
        """Test odporności na błędy w danych - nieprawidłowa trudność"""
        # Tworzymy plik z błędnymi danymi (difficulty jako tekst)
        with open(self.error_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'name': 'Good Trail', 'distance': '10.0', 'difficulty': '2', 'terrain': 'forest'})
            writer.writerow({'name': 'Bad Trail', 'distance': '5.0', 'difficulty': 'very_hard', 'terrain': 'mountain'})
        
        repository = FileRouteRepository(self.error_file_path)
        
        with self.assertRaises(DataParsingError) as context:
            repository.get_all()
        
        self.assertIn("Error parsing row 3", str(context.exception))
    
    def test_get_all_data_parsing_error_invalid_distance(self):
        """Test odporności na błędy w danych - nieprawidłowy dystans"""
        with open(self.error_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'name': 'Bad Trail', 'distance': 'very_long', 'difficulty': '3', 'terrain': 'mountain'})
        
        repository = FileRouteRepository(self.error_file_path)
        
        with self.assertRaises(DataParsingError) as context:
            repository.get_all()
        
        self.assertIn("Error parsing row 2", str(context.exception))
    
    def test_get_all_data_parsing_error_missing_column(self):
        """Test odporności na błędy w danych - brakująca kolumna"""
        with open(self.error_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty']  # Brakuje 'terrain'
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'name': 'Incomplete Trail', 'distance': '10.0', 'difficulty': '2'})
        
        repository = FileRouteRepository(self.error_file_path)
        
        with self.assertRaises(DataParsingError) as context:
            repository.get_all()
        
        self.assertIn("Error parsing row 2", str(context.exception))
    
    def test_get_all_data_parsing_error_negative_distance(self):
        """Test odporności na błędy w danych - ujemny dystans"""
        with open(self.error_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'name': 'Negative Trail', 'distance': '-5.0', 'difficulty': '2', 'terrain': 'forest'})
        
        repository = FileRouteRepository(self.error_file_path)
        
        with self.assertRaises(DataParsingError) as context:
            repository.get_all()
        
        self.assertIn("Error parsing row 2", str(context.exception))
    
    def test_get_all_empty_file(self):
        """Test pustego pliku CSV (tylko nagłówki)"""
        # Tworzymy pusty plik CSV z samymi nagłówkami
        with open(self.empty_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        
        repository = FileRouteRepository(self.empty_file_path)
        routes = repository.get_all()
        
        self.assertEqual(routes, [])
        self.assertIsInstance(routes, list)
    
    def test_get_all_file_not_found(self):
        """Test nieistniejącego pliku"""
        repository = FileRouteRepository(self.nonexistent_file_path)
        
        with self.assertRaises(FileNotFoundError) as context:
            repository.get_all()
        
        self.assertIn("File not found", str(context.exception))
        self.assertIn(self.nonexistent_file_path, str(context.exception))
    
    def test_get_all_completely_empty_file(self):
        """Test całkowicie pustego pliku (bez nagłówków)"""
        # Tworzymy całkowicie pusty plik
        with open(self.empty_file_path, 'w', encoding='utf-8') as file:
            pass  # Pusty plik
        
        repository = FileRouteRepository(self.empty_file_path)
        routes = repository.get_all()
        
        self.assertEqual(routes, [])
    
    def test_get_all_malformed_csv(self):
        """Test nieprawidłowo sformatowanego pliku CSV"""
        # Tworzymy plik z nieprawidłową strukturą CSV
        with open(self.error_file_path, 'w', encoding='utf-8') as file:
            file.write("This is not a CSV file\n")
            file.write("Just some random text\n")
        
        repository = FileRouteRepository(self.error_file_path)
        
        with self.assertRaises(DataParsingError) as context:
            repository.get_all()
        
        self.assertIn("Error parsing row 2", str(context.exception))
    
    def test_get_all_mixed_valid_invalid_data(self):
        """Test pliku z mieszanymi poprawnymi i nieprawidłowymi danymi"""
        with open(self.error_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'distance', 'difficulty', 'terrain']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'name': 'Good Trail 1', 'distance': '10.0', 'difficulty': '2', 'terrain': 'forest'})
            writer.writerow({'name': 'Good Trail 2', 'distance': '15.0', 'difficulty': '3', 'terrain': 'mountain'})
            writer.writerow({'name': 'Bad Trail', 'distance': '5.0', 'difficulty': 'invalid', 'terrain': 'desert'})
        
        repository = FileRouteRepository(self.error_file_path)
        
        # Powinien rzucić wyjątek przy pierwszym błędnym wierszu
        with self.assertRaises(DataParsingError) as context:
            repository.get_all()
        
        self.assertIn("Error parsing row 4", str(context.exception))
    
    def test_repository_constructor(self):
        """Test konstruktora FileRouteRepository"""
        repository = FileRouteRepository(self.test_file_path)
        self.assertEqual(repository.file_path, self.test_file_path)
    
    def test_get_all_unicode_characters(self):
        """Test obsługi znaków Unicode w danych"""
        test_data = [
            {'name': 'Szlak Gęsi', 'distance': '12.5', 'difficulty': '3', 'terrain': 'góry'},
            {'name': 'Ścieżka Żółwia', 'distance': '8.0', 'difficulty': '2', 'terrain': 'las'}
        ]
        
        self._create_valid_csv_file(self.test_file_path, test_data)
        
        repository = FileRouteRepository(self.test_file_path)
        routes = repository.get_all()
        
        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0].name, 'Szlak Gęsi')
        self.assertEqual(routes[0].terrain, 'góry')
        self.assertEqual(routes[1].name, 'Ścieżka Żółwia')
        self.assertEqual(routes[1].terrain, 'las')


if __name__ == '__main__':
    unittest.main() 