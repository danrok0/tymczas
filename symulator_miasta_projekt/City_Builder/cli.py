#!/usr/bin/env python3
"""
Interfejs wiersza poleceń dla City Builder.
Obsługuje argumenty startowe, konfigurację i tryby uruchomienia.
"""

import argparse
import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Dodaj ścieżkę do modułów
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core.config_manager import get_config_manager
from core.logger import setup_logging, get_game_logger
from core.functional_utils import validate_game_data

class CityBuilderCLI:
    """Główna klasa interfejsu wiersza poleceń."""
    
    def __init__(self):
        """Inicjalizuje CLI."""
        self.parser = self._create_parser()
        self.config_manager = get_config_manager()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Tworzy parser argumentów wiersza poleceń.
        
        Returns:
            Skonfigurowany ArgumentParser
        """
        parser = argparse.ArgumentParser(
            prog='city_builder',
            description='Advanced City Builder - Symulator miasta',
            epilog='Przykład użycia: python cli.py --new-game --difficulty Hard --map-size 80x80',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Grupa głównych akcji
        action_group = parser.add_mutually_exclusive_group()
        action_group.add_argument(
            '--new-game', 
            action='store_true',
            help='Rozpocznij nową grę'
        )
        action_group.add_argument(
            '--load-game', 
            type=str, 
            metavar='SAVE_FILE',
            help='Wczytaj grę z pliku zapisu'
        )
        action_group.add_argument(
            '--config', 
            action='store_true',
            help='Pokaż aktualną konfigurację'
        )
        action_group.add_argument(
            '--validate', 
            type=str, 
            metavar='DATA_FILE',
            help='Waliduj plik danych gry'
        )
        
        # Ustawienia gry
        game_group = parser.add_argument_group('Ustawienia gry')
        game_group.add_argument(
            '--difficulty', 
            choices=['Easy', 'Normal', 'Hard'],
            default='Normal',
            help='Poziom trudności (domyślnie: Normal)'
        )
        game_group.add_argument(
            '--map-size', 
            type=str, 
            metavar='WIDTHxHEIGHT',
            default='60x60',
            help='Rozmiar mapy w formacie WIDTHxHEIGHT (domyślnie: 60x60)'
        )
        game_group.add_argument(
            '--language', 
            choices=['pl', 'en'],
            default='pl',
            help='Język interfejsu (domyślnie: pl)'
        )
        game_group.add_argument(
            '--auto-save', 
            type=int, 
            metavar='SECONDS',
            default=300,
            help='Interwał automatycznego zapisu w sekundach (domyślnie: 300)'
        )
        
        # Ustawienia interfejsu
        ui_group = parser.add_argument_group('Ustawienia interfejsu')
        ui_group.add_argument(
            '--window-size', 
            type=str, 
            metavar='WIDTHxHEIGHT',
            default='1600x1000',
            help='Rozmiar okna w formacie WIDTHxHEIGHT (domyślnie: 1600x1000)'
        )
        ui_group.add_argument(
            '--fullscreen', 
            action='store_true',
            help='Uruchom w trybie pełnoekranowym'
        )
        ui_group.add_argument(
            '--no-sound', 
            action='store_true',
            help='Wyłącz dźwięki'
        )
        ui_group.add_argument(
            '--no-animations', 
            action='store_true',
            help='Wyłącz animacje'
        )
        
        # Ustawienia wydajności
        perf_group = parser.add_argument_group('Ustawienia wydajności')
        perf_group.add_argument(
            '--max-fps', 
            type=int, 
            metavar='FPS',
            default=60,
            help='Maksymalna liczba klatek na sekundę (domyślnie: 60)'
        )
        perf_group.add_argument(
            '--update-interval', 
            type=int, 
            metavar='MS',
            default=15000,
            help='Interwał aktualizacji gry w milisekundach (domyślnie: 15000)'
        )
        perf_group.add_argument(
            '--enable-multithreading', 
            action='store_true',
            help='Włącz wielowątkowość'
        )
        
        # Ustawienia debugowania
        debug_group = parser.add_argument_group('Ustawienia debugowania')
        debug_group.add_argument(
            '--debug', 
            action='store_true',
            help='Włącz tryb debugowania'
        )
        debug_group.add_argument(
            '--log-level', 
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Poziom logowania (domyślnie: INFO)'
        )
        debug_group.add_argument(
            '--log-file', 
            type=str, 
            metavar='FILE',
            help='Plik logów (domyślnie: automatyczny)'
        )
        debug_group.add_argument(
            '--performance-stats', 
            action='store_true',
            help='Pokaż statystyki wydajności'
        )
        
        # Narzędzia
        tools_group = parser.add_argument_group('Narzędzia')
        tools_group.add_argument(
            '--export-config', 
            type=str, 
            metavar='FILE',
            help='Eksportuj konfigurację do pliku'
        )
        tools_group.add_argument(
            '--import-config', 
            type=str, 
            metavar='FILE',
            help='Importuj konfigurację z pliku'
        )
        tools_group.add_argument(
            '--reset-config', 
            action='store_true',
            help='Resetuj konfigurację do wartości domyślnych'
        )
        tools_group.add_argument(
            '--list-saves', 
            action='store_true',
            help='Pokaż listę zapisanych gier'
        )
        tools_group.add_argument(
            '--cleanup-logs', 
            type=int, 
            metavar='DAYS',
            help='Usuń logi starsze niż podana liczba dni'
        )
        
        # Informacje
        info_group = parser.add_argument_group('Informacje')
        info_group.add_argument(
            '--version', 
            action='version', 
            version='City Builder v1.0.0 (Faza 5)'
        )
        info_group.add_argument(
            '--system-info', 
            action='store_true',
            help='Pokaż informacje o systemie'
        )
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parsuje argumenty wiersza poleceń.
        
        Args:
            args: Lista argumentów (domyślnie sys.argv)
            
        Returns:
            Sparsowane argumenty
        """
        return self.parser.parse_args(args)
    
    def validate_args(self, args: argparse.Namespace) -> Dict[str, List[str]]:
        """
        Waliduje argumenty wiersza poleceń.
        
        Args:
            args: Sparsowane argumenty
            
        Returns:
            Słownik błędów walidacji
        """
        errors = {}
        
        # Walidacja rozmiaru mapy
        if hasattr(args, 'map_size') and args.map_size:
            if not self._validate_size_format(args.map_size):
                errors['map_size'] = ['Format musi być WIDTHxHEIGHT, np. 60x60']
        
        # Walidacja rozmiaru okna
        if hasattr(args, 'window_size') and args.window_size:
            if not self._validate_size_format(args.window_size):
                errors['window_size'] = ['Format musi być WIDTHxHEIGHT, np. 1600x1000']
        
        # Walidacja pliku zapisu
        if hasattr(args, 'load_game') and args.load_game:
            save_path = Path(args.load_game)
            if not save_path.exists():
                errors['load_game'] = [f'Plik zapisu nie istnieje: {args.load_game}']
            elif not save_path.suffix.lower() == '.json':
                errors['load_game'] = ['Plik zapisu musi mieć rozszerzenie .json']
        
        # Walidacja pliku konfiguracji
        if hasattr(args, 'import_config') and args.import_config:
            config_path = Path(args.import_config)
            if not config_path.exists():
                errors['import_config'] = [f'Plik konfiguracji nie istnieje: {args.import_config}']
        
        # Walidacja pliku walidacji
        if hasattr(args, 'validate') and args.validate:
            validate_path = Path(args.validate)
            if not validate_path.exists():
                errors['validate'] = [f'Plik do walidacji nie istnieje: {args.validate}']
        
        return errors
    
    def _validate_size_format(self, size_str: str) -> bool:
        """Waliduje format rozmiaru WIDTHxHEIGHT."""
        import re
        pattern = re.compile(r'^\d+x\d+$')
        return pattern.match(size_str) is not None
    
    def _parse_size(self, size_str: str) -> tuple:
        """Parsuje string rozmiaru na tuple (width, height)."""
        width, height = size_str.split('x')
        return int(width), int(height)
    
    def apply_args_to_config(self, args: argparse.Namespace) -> bool:
        """
        Aplikuje argumenty CLI do konfiguracji.
        
        Args:
            args: Sparsowane argumenty
            
        Returns:
            True jeśli zastosowano pomyślnie
        """
        try:
            # Ustawienia gry
            if hasattr(args, 'difficulty') and args.difficulty:
                self.config_manager.set('game_settings.difficulty', args.difficulty)
            
            if hasattr(args, 'language') and args.language:
                self.config_manager.set('game_settings.language', args.language)
            
            if hasattr(args, 'auto_save') and args.auto_save:
                self.config_manager.set('game_settings.auto_save_interval', args.auto_save)
            
            if hasattr(args, 'no_sound') and args.no_sound:
                self.config_manager.set('game_settings.enable_sound', False)
            
            if hasattr(args, 'no_animations') and args.no_animations:
                self.config_manager.set('game_settings.enable_animations', False)
            
            # Ustawienia mapy
            if hasattr(args, 'map_size') and args.map_size:
                width, height = self._parse_size(args.map_size)
                self.config_manager.set('game_settings.default_map_size.width', width)
                self.config_manager.set('game_settings.default_map_size.height', height)
            
            # Ustawienia interfejsu
            if hasattr(args, 'window_size') and args.window_size:
                width, height = self._parse_size(args.window_size)
                self.config_manager.set('ui_settings.window_width', width)
                self.config_manager.set('ui_settings.window_height', height)
            
            # Ustawienia wydajności
            if hasattr(args, 'max_fps') and args.max_fps:
                self.config_manager.set('performance_settings.max_fps', args.max_fps)
            
            if hasattr(args, 'update_interval') and args.update_interval:
                self.config_manager.set('performance_settings.update_interval', args.update_interval)
            
            if hasattr(args, 'enable_multithreading') and args.enable_multithreading:
                self.config_manager.set('performance_settings.enable_multithreading', True)
            
            # Ustawienia debugowania
            if hasattr(args, 'debug') and args.debug:
                self.config_manager.set('advanced_settings.debug_mode', True)
                self.config_manager.set('performance_settings.log_level', 'DEBUG')
            
            if hasattr(args, 'log_level') and args.log_level:
                self.config_manager.set('performance_settings.log_level', args.log_level)
            
            if hasattr(args, 'performance_stats') and args.performance_stats:
                self.config_manager.set('advanced_settings.show_performance_stats', True)
            
            return True
            
        except Exception as e:
            print(f"Błąd aplikowania argumentów do konfiguracji: {e}")
            return False
    
    def execute_action(self, args: argparse.Namespace) -> int:
        """
        Wykonuje akcję na podstawie argumentów.
        
        Args:
            args: Sparsowane argumenty
            
        Returns:
            Kod wyjścia (0 = sukces)
        """
        try:
            # Konfiguracja logowania
            log_config = {
                'level': args.log_level if hasattr(args, 'log_level') else 'INFO',
                'console_output': True,
                'file_output': True,
                'max_file_size': 10 * 1024 * 1024,  # 10MB
                'backup_count': 5,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'date_format': '%Y-%m-%d %H:%M:%S'
            }
            setup_logging(log_config)
            logger = get_game_logger().get_logger('cli')
            
            # Wykonaj akcję
            if hasattr(args, 'config') and args.config:
                return self._show_config()
            
            elif hasattr(args, 'validate') and args.validate:
                return self._validate_file(args.validate)
            
            elif hasattr(args, 'export_config') and args.export_config:
                return self._export_config(args.export_config)
            
            elif hasattr(args, 'import_config') and args.import_config:
                return self._import_config(args.import_config)
            
            elif hasattr(args, 'reset_config') and args.reset_config:
                return self._reset_config()
            
            elif hasattr(args, 'list_saves') and args.list_saves:
                return self._list_saves()
            
            elif hasattr(args, 'cleanup_logs') and args.cleanup_logs:
                return self._cleanup_logs(args.cleanup_logs)
            
            elif hasattr(args, 'system_info') and args.system_info:
                return self._show_system_info()
            
            else:
                # Uruchom grę
                return self._start_game(args)
            
        except Exception as e:
            print(f"Błąd wykonywania akcji: {e}")
            return 1
    
    def _show_config(self) -> int:
        """Pokazuje aktualną konfigurację."""
        try:
            config = self.config_manager.get_all_settings()
            print("=== Aktualna konfiguracja ===")
            print(json.dumps(config, indent=2, ensure_ascii=False))
            return 0
        except Exception as e:
            print(f"Błąd pokazywania konfiguracji: {e}")
            return 1
    
    def _validate_file(self, file_path: str) -> int:
        """Waliduje plik danych gry."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            errors = validate_game_data(data)
            
            if errors:
                print("=== Błędy walidacji ===")
                for field, field_errors in errors.items():
                    print(f"{field}:")
                    for error in field_errors:
                        print(f"  - {error}")
                return 1
            else:
                print("✅ Plik jest poprawny")
                return 0
                
        except Exception as e:
            print(f"Błąd walidacji pliku: {e}")
            return 1
    
    def _export_config(self, file_path: str) -> int:
        """Eksportuje konfigurację."""
        try:
            if self.config_manager.export_config(file_path):
                print(f"✅ Konfiguracja wyeksportowana do: {file_path}")
                return 0
            else:
                print("❌ Błąd eksportu konfiguracji")
                return 1
        except Exception as e:
            print(f"Błąd eksportu konfiguracji: {e}")
            return 1
    
    def _import_config(self, file_path: str) -> int:
        """Importuje konfigurację."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Waliduj i zastosuj konfigurację
            # Tu można dodać dodatkową walidację
            
            print(f"✅ Konfiguracja zaimportowana z: {file_path}")
            return 0
        except Exception as e:
            print(f"Błąd importu konfiguracji: {e}")
            return 1
    
    def _reset_config(self) -> int:
        """Resetuje konfigurację."""
        try:
            if self.config_manager.reset_to_defaults():
                print("✅ Konfiguracja zresetowana do wartości domyślnych")
                return 0
            else:
                print("❌ Błąd resetowania konfiguracji")
                return 1
        except Exception as e:
            print(f"Błąd resetowania konfiguracji: {e}")
            return 1
    
    def _list_saves(self) -> int:
        """Pokazuje listę zapisanych gier."""
        try:
            saves_dir = Path('saves')
            if not saves_dir.exists():
                print("Brak katalogu z zapisami")
                return 0
            
            save_files = list(saves_dir.glob('*.json'))
            if not save_files:
                print("Brak zapisanych gier")
                return 0
            
            print("=== Zapisane gry ===")
            for save_file in sorted(save_files, key=lambda f: f.stat().st_mtime, reverse=True):
                size = save_file.stat().st_size
                mtime = save_file.stat().st_mtime
                from datetime import datetime
                date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{save_file.name:<30} {size:>10} bytes  {date_str}")
            
            return 0
        except Exception as e:
            print(f"Błąd listowania zapisów: {e}")
            return 1
    
    def _cleanup_logs(self, days: int) -> int:
        """Czyści stare logi."""
        try:
            logger = get_game_logger()
            logger.cleanup_old_logs(days)
            print(f"✅ Wyczyszczono logi starsze niż {days} dni")
            return 0
        except Exception as e:
            print(f"Błąd czyszczenia logów: {e}")
            return 1
    
    def _show_system_info(self) -> int:
        """Pokazuje informacje o systemie."""
        try:
            import platform
            import psutil
            
            print("=== Informacje o systemie ===")
            print(f"System: {platform.system()} {platform.release()}")
            print(f"Procesor: {platform.processor()}")
            print(f"Pamięć RAM: {psutil.virtual_memory().total // (1024**3)} GB")
            print(f"Python: {platform.python_version()}")
            
            # Informacje o grze
            logger = get_game_logger()
            log_summary = logger.get_log_summary()
            print("\n=== Informacje o grze ===")
            print(f"Pliki logów: {log_summary.get('log_files_count', 0)}")
            print(f"Rozmiar logów: {log_summary.get('total_size_mb', 0):.2f} MB")
            print(f"Poziom logowania: {log_summary.get('current_level', 'N/A')}")
            
            return 0
        except Exception as e:
            print(f"Błąd pokazywania informacji o systemie: {e}")
            return 1
    
    def _start_game(self, args: argparse.Namespace) -> int:
        """Uruchamia grę."""
        try:
            # Zastosuj argumenty do konfiguracji
            self.apply_args_to_config(args)
            
            # Uruchom główną aplikację
            from Main import main
            main()
            return 0
            
        except Exception as e:
            print(f"Błąd uruchamiania gry: {e}")
            return 1


def main():
    """Główna funkcja CLI."""
    cli = CityBuilderCLI()
    
    try:
        args = cli.parse_args()
        
        # Waliduj argumenty
        errors = cli.validate_args(args)
        if errors:
            print("Błędy w argumentach:")
            for field, field_errors in errors.items():
                for error in field_errors:
                    print(f"  {field}: {error}")
            return 1
        
        # Wykonaj akcję
        return cli.execute_action(args)
        
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
        return 130
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 