import unittest
import sys
import os

# Dodaj główny katalog do ścieżki Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Route, UserPreference


class TestRoute(unittest.TestCase):
    
    def test_route_constructor_valid_data(self):
        """Test tworzenia obiektu Route z poprawnymi danymi"""
        route = Route("Mountain Trail", 15.5, 3, "mountain")
        
        self.assertEqual(route.name, "Mountain Trail")
        self.assertEqual(route.distance, 15.5)
        self.assertEqual(route.difficulty, 3)
        self.assertEqual(route.terrain, "mountain")
    
    def test_route_constructor_integer_distance(self):
        """Test akceptowania dystansu jako liczby całkowitej"""
        route = Route("City Walk", 10, 1, "urban")
        self.assertEqual(route.distance, 10)
    
    def test_route_constructor_empty_name(self):
        """Test rzucania ValueError dla pustej nazwy"""
        with self.assertRaises(ValueError) as context:
            Route("", 10.0, 2, "forest")
        self.assertIn("Name must be a non-empty string", str(context.exception))
    
    def test_route_constructor_whitespace_name(self):
        """Test rzucania ValueError dla nazwy składającej się tylko z białych znaków"""
        with self.assertRaises(ValueError) as context:
            Route("   ", 10.0, 2, "forest")
        self.assertIn("Name must be a non-empty string", str(context.exception))
    
    def test_route_constructor_non_string_name(self):
        """Test rzucania ValueError dla nazwy, która nie jest stringiem"""
        with self.assertRaises(ValueError) as context:
            Route(123, 10.0, 2, "forest")
        self.assertIn("Name must be a non-empty string", str(context.exception))
    
    def test_route_constructor_negative_distance(self):
        """Test rzucania ValueError dla ujemnego dystansu"""
        with self.assertRaises(ValueError) as context:
            Route("Trail", -5.0, 2, "forest")
        self.assertIn("Distance must be a non-negative number", str(context.exception))
    
    def test_route_constructor_zero_distance(self):
        """Test akceptowania zerowego dystansu"""
        route = Route("Start Point", 0, 1, "park")
        self.assertEqual(route.distance, 0)
    
    def test_route_constructor_invalid_distance_type(self):
        """Test rzucania ValueError dla nieprawidłowego typu dystansu"""
        with self.assertRaises(ValueError) as context:
            Route("Trail", "10km", 2, "forest")
        self.assertIn("Distance must be a non-negative number", str(context.exception))
    
    def test_route_constructor_difficulty_too_low(self):
        """Test rzucania ValueError dla trudności poniżej 1"""
        with self.assertRaises(ValueError) as context:
            Route("Easy Trail", 5.0, 0, "forest")
        self.assertIn("Difficulty must be an integer between 1 and 5", str(context.exception))
    
    def test_route_constructor_difficulty_too_high(self):
        """Test rzucania ValueError dla trudności powyżej 5"""
        with self.assertRaises(ValueError) as context:
            Route("Extreme Trail", 20.0, 6, "mountain")
        self.assertIn("Difficulty must be an integer between 1 and 5", str(context.exception))
    
    def test_route_constructor_difficulty_float(self):
        """Test rzucania ValueError dla trudności jako liczby zmiennoprzecinkowej"""
        with self.assertRaises(ValueError) as context:
            Route("Trail", 10.0, 2.5, "forest")
        self.assertIn("Difficulty must be an integer between 1 and 5", str(context.exception))
    
    def test_route_constructor_valid_difficulty_boundaries(self):
        """Test akceptowania trudności na granicach (1 i 5)"""
        route1 = Route("Easy", 5.0, 1, "park")
        route2 = Route("Hard", 15.0, 5, "mountain")
        
        self.assertEqual(route1.difficulty, 1)
        self.assertEqual(route2.difficulty, 5)
    
    def test_route_constructor_empty_terrain(self):
        """Test rzucania ValueError dla pustego terenu"""
        with self.assertRaises(ValueError) as context:
            Route("Trail", 10.0, 2, "")
        self.assertIn("Terrain must be a non-empty string", str(context.exception))
    
    def test_route_constructor_whitespace_terrain(self):
        """Test rzucania ValueError dla terenu składającego się tylko z białych znaków"""
        with self.assertRaises(ValueError) as context:
            Route("Trail", 10.0, 2, "   ")
        self.assertIn("Terrain must be a non-empty string", str(context.exception))
    
    def test_route_constructor_non_string_terrain(self):
        """Test rzucania ValueError dla terenu, który nie jest stringiem"""
        with self.assertRaises(ValueError) as context:
            Route("Trail", 10.0, 2, 123)
        self.assertIn("Terrain must be a non-empty string", str(context.exception))
    
    def test_route_equality(self):
        """Test porównywania obiektów Route"""
        route1 = Route("Trail A", 10.0, 3, "forest")
        route2 = Route("Trail A", 10.0, 3, "forest")
        route3 = Route("Trail B", 10.0, 3, "forest")
        
        self.assertEqual(route1, route2)
        self.assertNotEqual(route1, route3)
        self.assertNotEqual(route1, "not a route")
    
    def test_route_repr(self):
        """Test reprezentacji tekstowej obiektu Route"""
        route = Route("Test Trail", 12.5, 4, "mountain")
        expected = "Route(name='Test Trail', distance=12.5, difficulty=4, terrain='mountain')"
        self.assertEqual(repr(route), expected)


class TestUserPreference(unittest.TestCase):
    
    def test_user_preference_constructor_default_values(self):
        """Test tworzenia obiektu UserPreference z domyślnymi wartościami"""
        pref = UserPreference()
        
        self.assertIsNone(pref.max_difficulty)
        self.assertIsNone(pref.terrain)
        self.assertIsNone(pref.max_distance)
    
    def test_user_preference_constructor_all_parameters(self):
        """Test tworzenia obiektu UserPreference ze wszystkimi parametrami"""
        pref = UserPreference(max_difficulty=3, terrain="mountain", max_distance=20.0)
        
        self.assertEqual(pref.max_difficulty, 3)
        self.assertEqual(pref.terrain, "mountain")
        self.assertEqual(pref.max_distance, 20.0)
    
    def test_user_preference_constructor_partial_parameters(self):
        """Test tworzenia obiektu UserPreference z częściowymi parametrami"""
        pref = UserPreference(max_difficulty=2, terrain="forest")
        
        self.assertEqual(pref.max_difficulty, 2)
        self.assertEqual(pref.terrain, "forest")
        self.assertIsNone(pref.max_distance)
    
    def test_user_preference_max_difficulty_too_low(self):
        """Test rzucania ValueError dla max_difficulty poniżej 1"""
        with self.assertRaises(ValueError) as context:
            UserPreference(max_difficulty=0)
        self.assertIn("Max difficulty must be an integer between 1 and 5", str(context.exception))
    
    def test_user_preference_max_difficulty_too_high(self):
        """Test rzucania ValueError dla max_difficulty powyżej 5"""
        with self.assertRaises(ValueError) as context:
            UserPreference(max_difficulty=6)
        self.assertIn("Max difficulty must be an integer between 1 and 5", str(context.exception))
    
    def test_user_preference_max_difficulty_float(self):
        """Test rzucania ValueError dla max_difficulty jako liczby zmiennoprzecinkowej"""
        with self.assertRaises(ValueError) as context:
            UserPreference(max_difficulty=2.5)
        self.assertIn("Max difficulty must be an integer between 1 and 5", str(context.exception))
    
    def test_user_preference_max_difficulty_boundaries(self):
        """Test akceptowania max_difficulty na granicach (1 i 5)"""
        pref1 = UserPreference(max_difficulty=1)
        pref2 = UserPreference(max_difficulty=5)
        
        self.assertEqual(pref1.max_difficulty, 1)
        self.assertEqual(pref2.max_difficulty, 5)
    
    def test_user_preference_empty_terrain(self):
        """Test rzucania ValueError dla pustego terenu"""
        with self.assertRaises(ValueError) as context:
            UserPreference(terrain="")
        self.assertIn("Terrain must be a non-empty string", str(context.exception))
    
    def test_user_preference_whitespace_terrain(self):
        """Test rzucania ValueError dla terenu składającego się tylko z białych znaków"""
        with self.assertRaises(ValueError) as context:
            UserPreference(terrain="   ")
        self.assertIn("Terrain must be a non-empty string", str(context.exception))
    
    def test_user_preference_non_string_terrain(self):
        """Test rzucania ValueError dla terenu, który nie jest stringiem"""
        with self.assertRaises(ValueError) as context:
            UserPreference(terrain=123)
        self.assertIn("Terrain must be a non-empty string", str(context.exception))
    
    def test_user_preference_negative_max_distance(self):
        """Test rzucania ValueError dla ujemnego max_distance"""
        with self.assertRaises(ValueError) as context:
            UserPreference(max_distance=-5.0)
        self.assertIn("Max distance must be a non-negative number", str(context.exception))
    
    def test_user_preference_zero_max_distance(self):
        """Test akceptowania zerowego max_distance"""
        pref = UserPreference(max_distance=0)
        self.assertEqual(pref.max_distance, 0)
    
    def test_user_preference_invalid_max_distance_type(self):
        """Test rzucania ValueError dla nieprawidłowego typu max_distance"""
        with self.assertRaises(ValueError) as context:
            UserPreference(max_distance="10km")
        self.assertIn("Max distance must be a non-negative number", str(context.exception))
    
    def test_user_preference_repr(self):
        """Test reprezentacji tekstowej obiektu UserPreference"""
        pref = UserPreference(max_difficulty=3, terrain="forest", max_distance=15.0)
        expected = "UserPreference(max_difficulty=3, terrain='forest', max_distance=15.0)"
        self.assertEqual(repr(pref), expected)


if __name__ == '__main__':
    unittest.main() 