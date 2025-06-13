"""
Moduł zarządzania konfiguracją aplikacji.
Obsługuje wczytywanie, zapisywanie i walidację ustawień z pliku JSON.
"""

import json
import os
import re
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
import copy

class ConfigManager:
    """Menedżer konfiguracji aplikacji z walidacją i obsługą błędów."""
    
    def __init__(self, config_path: str = "data/config.json"):
        """
        Inicjalizuje menedżer konfiguracji.
        
        Args:
            config_path: Ścieżka do pliku konfiguracyjnego
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.default_config = self._get_default_config()
        self.validators = self._setup_validators()
        
        # Konfiguracja logowania
        self.logger = logging.getLogger(__name__)
        
        # Wczytaj konfigurację
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Zwraca domyślną konfigurację."""
        return {
            "game_settings": {
                "default_map_size": {"width": 60, "height": 60},
                "auto_save_interval": 300,
                "difficulty": "Normal",
                "language": "pl",
                "enable_sound": True,
                "enable_animations": True,
                "show_tooltips": True
            },
            "ui_settings": {
                "window_width": 1600,
                "window_height": 1000,
                "tile_size": 32,
                "zoom_levels": [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
                "default_zoom": 1.0,
                "show_grid": True,
                "show_building_effects": True
            },
            "performance_settings": {
                "max_fps": 60,
                "update_interval": 15000,
                "enable_multithreading": False,
                "cache_size": 100,
                "log_level": "INFO"
            },
            "database_settings": {
                "db_path": "city_builder.db",
                "backup_interval": 3600,
                "max_backups": 5
            },
            "export_settings": {
                "default_export_format": "CSV",
                "export_path": "exports/",
                "include_charts": True,
                "chart_format": "PNG"
            },
            "advanced_settings": {
                "debug_mode": False,
                "show_performance_stats": False,
                "enable_cheats": False,
                "custom_building_path": "assets/custom_buildings/",
                "mod_support": False
            }
        }
    
    def _setup_validators(self) -> Dict[str, re.Pattern]:
        """Konfiguruje walidatory regex dla różnych typów danych."""
        return {
            'difficulty': re.compile(r'^(Easy|Normal|Hard)$'),
            'language': re.compile(r'^[a-z]{2}$'),
            'log_level': re.compile(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$'),
            'export_format': re.compile(r'^(CSV|JSON|XML|XLSX)$'),
            'chart_format': re.compile(r'^(PNG|JPG|JPEG|SVG|PDF)$'),
            'file_path': re.compile(r'^[a-zA-Z0-9_\-./\\]+\.(db|json|csv|xml)$'),
            'directory_path': re.compile(r'^[a-zA-Z0-9_\-./\\]+[/\\]?$'),  # Akceptuj oba separatory
            'positive_int': re.compile(r'^[1-9]\d*$'),
            'positive_float': re.compile(r'^[0-9]*\.?[0-9]+$'),
            'boolean_string': re.compile(r'^(true|false|True|False|1|0)$')
        }
    
    def validate_value(self, key: str, value: Any) -> bool:
        """
        Waliduje wartość używając wyrażeń regularnych.
        
        Args:
            key: Klucz konfiguracji
            value: Wartość do walidacji
            
        Returns:
            True jeśli wartość jest poprawna
        """
        try:
            # Konwertuj wartość na string dla regex
            str_value = str(value)
            
            # Mapowanie kluczy na walidatory
            validation_map = {
                'difficulty': 'difficulty',
                'language': 'language',
                'log_level': 'log_level',
                'default_export_format': 'export_format',
                'chart_format': 'chart_format',
                'db_path': 'file_path',
                'export_path': 'directory_path',
                'custom_building_path': 'directory_path'
            }
            
            # Walidacja numeryczna
            if key in ['window_width', 'window_height', 'tile_size', 'max_fps', 
                      'update_interval', 'cache_size', 'auto_save_interval', 
                      'backup_interval', 'max_backups']:
                return self.validators['positive_int'].match(str_value) is not None
            
            # Walidacja float
            if key in ['default_zoom'] or 'zoom_levels' in key:
                return self.validators['positive_float'].match(str_value) is not None
            
            # Walidacja boolean
            if isinstance(value, bool):
                return True
            
            # Walidacja specyficzna
            if key in validation_map:
                validator_key = validation_map[key]
                return self.validators[validator_key].match(str_value) is not None
            
            return True  # Domyślnie akceptuj
            
        except Exception as e:
            self.logger.warning(f"Błąd walidacji dla {key}: {e}")
            return False
    
    def load_config(self) -> bool:
        """
        Wczytuje konfigurację z pliku JSON.
        
        Returns:
            True jeśli wczytano pomyślnie
        """
        try:
            if not self.config_path.exists():
                self.logger.info("Plik konfiguracyjny nie istnieje, tworzę domyślny")
                self.config = self.default_config.copy()
                self.save_config()
                return True
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Waliduj wczytaną konfigurację
            if self._validate_config(loaded_config):
                self.config = self._merge_with_defaults(loaded_config)
                self.logger.info("Konfiguracja wczytana pomyślnie")
                return True
            else:
                self.logger.warning("Niepoprawna konfiguracja, używam domyślnej")
                self.config = self.default_config.copy()
                return False
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Błąd parsowania JSON: {e}")
            self.config = self.default_config.copy()
            return False
        except Exception as e:
            self.logger.error(f"Błąd wczytywania konfiguracji: {e}")
            self.config = self.default_config.copy()
            return False
    
    def save_config(self) -> bool:
        """
        Zapisuje konfigurację do pliku JSON.
        
        Returns:
            True jeśli zapisano pomyślnie
        """
        try:
            # Upewnij się, że katalog istnieje
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.logger.info("Konfiguracja zapisana pomyślnie")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd zapisywania konfiguracji: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Pobiera wartość z konfiguracji używając ścieżki z kropkami.
        
        Args:
            key_path: Ścieżka do klucza (np. "game_settings.difficulty")
            default: Wartość domyślna
            
        Returns:
            Wartość z konfiguracji lub default
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                value = value[key]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Ustawia wartość w konfiguracji używając ścieżki z kropkami.
        
        Args:
            key_path: Ścieżka do klucza (np. "game_settings.difficulty")
            value: Nowa wartość
            
        Returns:
            True jeśli ustawiono pomyślnie
        """
        try:
            keys = key_path.split('.')
            
            # Waliduj wartość
            if not self.validate_value(keys[-1], value):
                self.logger.warning(f"Niepoprawna wartość dla {key_path}: {value}")
                return False
            
            # Nawiguj do odpowiedniego miejsca
            current = self.config
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Ustaw wartość
            current[keys[-1]] = value
            self.logger.info(f"Ustawiono {key_path} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd ustawiania {key_path}: {e}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Waliduje strukturę konfiguracji."""
        required_sections = ['game_settings', 'ui_settings', 'performance_settings']
        
        for section in required_sections:
            if section not in config:
                return False
        
        return True
    
    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """Łączy wczytaną konfigurację z domyślną."""
        merged = self.default_config.copy()
        
        def deep_merge(default: Dict, loaded: Dict) -> Dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(merged, loaded_config)
    
    def reset_to_defaults(self) -> bool:
        """Resetuje konfigurację do wartości domyślnych."""
        try:
            # Wygeneruj świeżą kopię domyślnej konfiguracji
            self.config = copy.deepcopy(self._get_default_config())
            self.save_config()
            self.logger.info("Konfiguracja zresetowana do domyślnych wartości")
            return True
        except Exception as e:
            self.logger.error(f"Błąd resetowania konfiguracji: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """Eksportuje konfigurację do pliku."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Błąd eksportu konfiguracji: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Zwraca wszystkie ustawienia."""
        return self.config.copy()


# Singleton instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Zwraca singleton instancję ConfigManager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager 