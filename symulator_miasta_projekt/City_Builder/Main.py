import sys
import os
import logging
import time

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Inicjalizuj systemy konfiguracji i logowania
from core.config_manager import get_config_manager
from core.logger import setup_logging, get_game_logger
from core.functional_utils import performance_monitor, safe_map, safe_filter

# Konfiguruj logowanie
config_manager = get_config_manager()
log_config = {
    'level': config_manager.get('advanced_settings.log_level', 'INFO'),
    'console_output': True,
    'file_output': True,
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}
setup_logging(log_config)
game_logger = get_game_logger()

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QMenuBar, QStatusBar, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, QTimer
from core.game_engine import GameEngine
from gui.map_canvas import MapCanvas
from gui.build_panel import BuildPanel
from core.events import EventManager
from gui.event_dialog import EventDialog
from gui.reports_panel import ReportsPanel
from core.technology import TechnologyManager
from gui.technology_panel import TechnologyPanel
from db.database import Database
from core.objectives import ObjectiveManager
from gui.objectives_panel import ObjectivesPanel

# Enable high DPI scaling
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

class MainWindow(QMainWindow):
    @performance_monitor
    def __init__(self):
        super().__init__()
        
        # Pobierz ustawienia z konfiguracji
        window_width = config_manager.get('ui_settings.window_width', 1600)
        window_height = config_manager.get('ui_settings.window_height', 1000)
        map_width = config_manager.get('game_settings.default_map_size.width', 60)
        map_height = config_manager.get('game_settings.default_map_size.height', 60)
        
        self.setWindowTitle("City Builder - Advanced City Simulator")
        self.setGeometry(100, 100, window_width, window_height)
        
        # Loguj inicjalizację
        logger = game_logger.get_logger('ui')
        logger.info(f"Inicjalizacja okna głównego {window_width}x{window_height}")
        game_logger.log_game_event('INIT', 'Uruchomienie aplikacji', {
            'window_size': f"{window_width}x{window_height}",
            'map_size': f"{map_width}x{map_height}"
        })
        
        # Create game engine
        self.game_engine = GameEngine(map_width=map_width, map_height=map_height)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create map canvas
        self.map_canvas = MapCanvas(self.game_engine.city_map)
        # Initialize resources in map_canvas
        self.map_canvas.resources = self.game_engine.economy.get_resource_amount('money')
        main_layout.addWidget(self.map_canvas, stretch=3)
        
        # Create build panel
        self.build_panel = BuildPanel(self.game_engine)
        # Initialize resources display
        self.build_panel.update_resources(self.game_engine.economy)
        
        # Initialize economy panel
        buildings = self.game_engine.get_all_buildings()
        income = self.game_engine.economy.calculate_taxes(buildings, self.game_engine.population)
        expenses = self.game_engine.economy.calculate_expenses(buildings, self.game_engine.population)
        tax_rates = self.game_engine.economy.tax_rates
        self.build_panel.update_economy_panel(income, expenses, tax_rates)
        
        main_layout.addWidget(self.build_panel, stretch=2)
        
        # Connect signals
        self.build_panel.building_selected.connect(self.map_canvas.select_building)
        self.build_panel.clear_selection.connect(self.on_clear_selection)
        self.map_canvas.building_placed.connect(self.on_building_placed)
        self.build_panel.rotate_btn.clicked.connect(self.map_canvas.rotate_building)
        self.map_canvas.building_sell_requested.connect(self.on_building_sell_requested)
        self.build_panel.sell_building_clicked.connect(self.on_building_sell_button)
        
        # Set focus on map canvas for keyboard events
        self.map_canvas.setFocus()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
        # Game loop timer - wolniejsze aktualizacje
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(15000)  # Update every 15 seconds
        
        # Create event manager
        self.event_manager = EventManager()
        
        # Create reports panel
        self.reports_panel = ReportsPanel()
        
        # Create technology tree and panel
        self.technology_tree = TechnologyManager()
        self.technology_panel = TechnologyPanel(self.technology_tree, self.game_engine)
        
        # Create database instance
        self.database = Database()
        
        # Create objectives system
        self.objective_manager = ObjectiveManager()
        self.objectives_panel = ObjectivesPanel(self.objective_manager)
        
        # Connect objective completion signal
        self.objectives_panel.objective_completed.connect(self.on_objective_completed)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        new_game_action = file_menu.addAction("New Game")
        load_game_action = file_menu.addAction("Load Game")
        save_game_action = file_menu.addAction("Save Game")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        
        # Game menu
        game_menu = menubar.addMenu("Game")
        pause_action = game_menu.addAction("Pause/Resume")
        game_menu.addSeparator()
        
        difficulty_menu = game_menu.addMenu("Difficulty")
        easy_action = difficulty_menu.addAction("Easy")
        normal_action = difficulty_menu.addAction("Normal")
        hard_action = difficulty_menu.addAction("Hard")
        
        # View menu
        view_menu = menubar.addMenu("View")
        reports_action = view_menu.addAction("Reports")
        alerts_action = view_menu.addAction("Alerts")
        
        # Technology menu
        technology_action = menubar.addAction("Technologie")
        
        # Objectives menu
        objectives_action = menubar.addAction("Cele")
        
        # Trade menu
        trade_action = menubar.addAction("Handel")
        
        # Achievements menu
        achievements_action = menubar.addAction("Osiągnięcia")
        
        # Connect actions
        exit_action.triggered.connect(self.close)
        new_game_action.triggered.connect(self.new_game)
        save_game_action.triggered.connect(self.save_game)
        load_game_action.triggered.connect(self.load_game)
        pause_action.triggered.connect(self.toggle_pause)
        
        # Difficulty actions
        easy_action.triggered.connect(lambda: self.set_difficulty("Easy"))
        normal_action.triggered.connect(lambda: self.set_difficulty("Normal"))
        hard_action.triggered.connect(lambda: self.set_difficulty("Hard"))
        
        # Reports action
        reports_action.triggered.connect(self.show_reports)
        
        # Technology action
        technology_action.triggered.connect(self.show_technology)
        
        # Objectives action
        objectives_action.triggered.connect(self.show_objectives)
        
        # Trade action
        trade_action.triggered.connect(self.show_trade)
        
        # Achievements action
        achievements_action.triggered.connect(self.show_achievements)
    
    def new_game(self):
        """Start a new game"""
        reply = QMessageBox.question(self, 'New Game', 
                                   'Are you sure you want to start a new game? Current progress will be lost.',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.game_engine = GameEngine(map_width=60, map_height=60)
            self.map_canvas.city_map = self.game_engine.city_map
            self.map_canvas.draw_map()
            
            # Update city level info for new game
            current_pop = self.game_engine.population.get_total_population()
            next_level_pop = self.game_engine.get_next_level_requirement()
            self.build_panel.update_city_level_info(
                self.game_engine.city_level,
                current_pop,
                next_level_pop
            )
            
            # Update other UI elements
            self.build_panel.update_resources(self.game_engine.economy)
            self.map_canvas.resources = self.game_engine.economy.get_resource_amount('money')
            
            # Update building availability
            self.build_panel.refresh_building_availability()
            
            self.update_status_bar()
    
    def save_game(self):
        """Save current game"""
        from PyQt6.QtWidgets import QInputDialog, QFileDialog
        import os
        
        # Ensure saves directory exists
        saves_dir = os.path.join(os.path.dirname(__file__), 'saves')
        os.makedirs(saves_dir, exist_ok=True)
        
        filename, ok = QInputDialog.getText(self, 'Zapisz Grę', 'Podaj nazwę zapisu:')
        if ok and filename:
            # Add .json extension if not present
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(saves_dir, filename)
            success = self.game_engine.save_game(filepath)
            if success:
                QMessageBox.information(self, 'Zapisz Grę', f'Gra zapisana jako {filename}')
            else:
                QMessageBox.warning(self, 'Zapisz Grę', 'Nie udało się zapisać gry')
    
    def load_game(self):
        """Load a saved game"""
        from PyQt6.QtWidgets import QFileDialog
        import os
        
        saves_dir = os.path.join(os.path.dirname(__file__), 'saves')
        if not os.path.exists(saves_dir):
            QMessageBox.warning(self, 'Wczytaj Grę', 'Brak zapisanych gier')
            return
        
        # Show file dialog to select save file
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            'Wybierz zapis gry', 
            saves_dir, 
            'Pliki zapisów (*.json);;Wszystkie pliki (*)'
        )
        
        if filepath:
            success = self.game_engine.load_game(filepath)
            if success:
                # Update all UI elements after loading
                self.map_canvas.city_map = self.game_engine.city_map
                self.map_canvas.draw_map()
                
                # Update resources display
                self.build_panel.update_resources(self.game_engine.economy)
                self.map_canvas.resources = self.game_engine.economy.get_resource_amount('money')
                
                # Update economy panel
                buildings = self.game_engine.get_all_buildings()
                income = self.game_engine.economy.calculate_taxes(buildings, self.game_engine.population)
                expenses = self.game_engine.economy.calculate_expenses(buildings, self.game_engine.population)
                tax_rates = self.game_engine.economy.tax_rates
                self.build_panel.update_economy_panel(income, expenses, tax_rates)
                
                # Update building availability
                self.build_panel.refresh_building_availability()
                
                # Update city level info
                current_pop = self.game_engine.population.get_total_population()
                next_level_pop = self.game_engine.get_next_level_requirement()
                self.build_panel.update_city_level_info(
                    self.game_engine.city_level,
                    current_pop,
                    next_level_pop
                )
                
                # Reset objectives for loaded game
                from core.objectives import ObjectiveManager
                from gui.objectives_panel import ObjectivesPanel
                
                self.objective_manager = ObjectiveManager()
                
                # Close old objectives panel if exists
                if hasattr(self, 'objectives_panel') and self.objectives_panel:
                    try:
                        self.objectives_panel.close()
                    except:
                        pass
                
                self.objectives_panel = ObjectivesPanel(self.objective_manager)
                self.objectives_panel.objective_completed.connect(self.on_objective_completed)
                
                # Clear reports history for loaded game
                self.reports_panel.history_data = {
                    'turns': [],
                    'population': [],
                    'budget': [],
                    'satisfaction': [],
                    'unemployment': [],
                    'income': [],
                    'expenses': []
                }
                self.reports_panel.update_charts()
                
                self.update_status_bar()
                QMessageBox.information(self, 'Wczytaj Grę', 'Gra wczytana pomyślnie')
            else:
                QMessageBox.warning(self, 'Wczytaj Grę', 'Nie udało się wczytać gry')
    
    def toggle_pause(self):
        """Toggle game pause state"""
        if self.game_engine.paused:
            self.game_engine.resume_game()
        else:
            self.game_engine.pause_game()
        self.update_status_bar()
    
    def set_difficulty(self, difficulty: str):
        """Set game difficulty"""
        self.game_engine.set_difficulty(difficulty)
        self.update_status_bar()
    
    def on_building_placed(self, x: int, y: int, building):
        """Handles building placement"""
        # Use game engine to place building
        success = self.game_engine.place_building(x, y, building)
        if success:
            # Update resources display
            self.build_panel.update_resources(self.game_engine.economy)
            self.map_canvas.resources = self.game_engine.economy.get_resource_amount('money')
            self.update_status_bar()
            
            # --- Nowy kod: aktualizacja panelu ekonomii ---
            buildings = self.game_engine.get_all_buildings()
            income = self.game_engine.economy.calculate_taxes(buildings, self.game_engine.population)
            expenses = self.game_engine.economy.calculate_expenses(buildings, self.game_engine.population)
            tax_rates = self.game_engine.economy.tax_rates
            self.build_panel.update_economy_panel(income, expenses, tax_rates)
        
        # Always redraw map after placement attempt
        self.map_canvas.draw_map()
    
    def on_clear_selection(self):
        """Handles clearing building selection"""
        self.map_canvas.select_building(None)
    
    @performance_monitor
    def update_game(self):
        """Main game loop - updates all city systems"""
        start_time = time.time()
        logger = game_logger.get_logger('game_engine')
        
        try:
            # Update game engine (handles economy, population, etc.)
            self.game_engine.update_turn()
            
            # Update UI elements
            self.update_status_bar()
            
            # Update build panel resources
            self.build_panel.update_resources(self.game_engine.economy)
            self.map_canvas.resources = self.game_engine.economy.get_resource_amount('money')
            
            # Update building availability
            self.build_panel.refresh_building_availability()
            
            # Update city level information
            current_pop = self.game_engine.population.get_total_population()
            next_level_pop = self.game_engine.get_next_level_requirement()
            self.build_panel.update_city_level_info(
                self.game_engine.city_level,
                current_pop,
                next_level_pop
            )
            
            # Update economy panel
            buildings = self.game_engine.get_all_buildings()
            income = self.game_engine.economy.calculate_taxes(buildings, self.game_engine.population)
            expenses = self.game_engine.economy.calculate_expenses(buildings, self.game_engine.population)
            tax_rates = self.game_engine.economy.tax_rates
            self.build_panel.update_economy_panel(income, expenses, tax_rates)
            
            # Update objectives system
            game_state = {
                'turn': self.game_engine.turn,
                'population': self.game_engine.population.get_total_population(),
                'money': self.game_engine.economy.get_resource_amount('money'),
                'satisfaction': self.game_engine.population.get_average_satisfaction(),
                'buildings': self.game_engine.get_all_buildings(),
                'unlocked_technologies': [tech.name for tech in self.technology_tree.technologies.values() if tech.is_researched]
            }
            self.objectives_panel.update_objectives(game_state)
            
            # Update reports with proper data using functional programming
            buildings = self.game_engine.get_all_buildings()
            income = self.game_engine.economy.calculate_taxes(buildings, self.game_engine.population)
            expenses = self.game_engine.economy.calculate_expenses(buildings, self.game_engine.population)
            
            self.reports_panel.add_data_point(
                turn=self.game_engine.turn,
                population=self.game_engine.population.get_total_population(),
                budget=self.game_engine.economy.get_resource_amount('money'),
                satisfaction=self.game_engine.population.get_average_satisfaction(),
                unemployment=self.game_engine.population.get_unemployment_rate(),
                income=income,
                expenses=expenses
            )
            self.reports_panel.update_charts()
            
            # Trigger random event (zmieniam częstotliwość i dodaję kontekst)
            if self.game_engine.turn % 8 == 0 and self.game_engine.turn > 0:  # Co 8 tur
                event = self.event_manager.trigger_random_event(game_state)
                game_logger.log_game_event('EVENT', f'Wydarzenie: {event.title}')
                dialog = EventDialog(event, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_option = dialog.selected_option
                    
                    # Apply decision-specific effects using functional programming
                    effects = self.event_manager.apply_decision_effects(event, selected_option)
                    
                    # Użyj map do przetworzenia efektów
                    effect_results = list(safe_map(
                        lambda effect_item: self._apply_event_effect(effect_item[0], effect_item[1]),
                        effects.items()
                    ))
                    
                    # Show event result
                    self.game_engine.add_alert(f"Wydarzenie: {event.title} - Wybrano: {selected_option}")
            
            # Save game state - naprawiam odwołania
            self.database.save_game_state(
                self.game_engine.population.get_total_population(),
                self.game_engine.economy.get_resource_amount('money'),
                int(self.game_engine.population.get_average_satisfaction()),
                str(self.game_engine.economy.get_resource_amount('money'))  # Konwertuję na string
            )

            # Save history - naprawiam odwołania
            self.database.save_history(
                self.game_engine.turn,
                self.game_engine.population.get_total_population(),
                self.game_engine.economy.get_resource_amount('money'),
                int(self.game_engine.population.get_average_satisfaction()),
                str(self.game_engine.economy.get_resource_amount('money'))  # Konwertuję na string
            )

            # Save statistics - naprawiam odwołania
            self.database.save_statistics('population', self.game_engine.population.get_total_population())
            self.database.save_statistics('money', self.game_engine.economy.get_resource_amount('money'))
            self.database.save_statistics('satisfaction', int(self.game_engine.population.get_average_satisfaction()))
            self.database.save_statistics('resources', self.game_engine.economy.get_resource_amount('money'))

            # Redraw map if needed
            self.map_canvas.draw_map()
            
            # Loguj wydajność aktualizacji
            update_time = time.time() - start_time
            game_logger.log_performance('game_update', update_time, {
                'population': current_pop,
                'buildings': len(self.game_engine.get_all_buildings())
            })
            
        except Exception as e:
            logger.error(f"Error in update_game: {e}")
            game_logger.log_error(e, 'update_game', {
                'turn': getattr(self.game_engine, 'turn', 0)
            })
    
    def _apply_event_effect(self, effect_type: str, effect_value: float) -> bool:
        """
        Aplikuje efekt wydarzenia.
        
        Args:
            effect_type: Typ efektu
            effect_value: Wartość efektu
            
        Returns:
            True jeśli efekt został zastosowany
        """
        try:
            if effect_type == "population":
                self.game_engine.population.add_instant_population(effect_value)
                return True
            elif effect_type == "satisfaction":
                # Dodaję wpływ na zadowolenie wszystkich grup
                for group in self.game_engine.population.groups.values():
                    group.satisfaction = max(0, min(100, group.satisfaction + effect_value))
                return True
            elif effect_type == "money":
                if effect_value > 0:
                    self.game_engine.economy.earn_money(effect_value)
                else:
                    self.game_engine.economy.spend_money(abs(effect_value))
                return True
            return False
        except Exception as e:
            game_logger.log_error(e, f'apply_event_effect_{effect_type}')
            return False
    
    def update_status_bar(self):
        """Update status bar with current city information"""
        summary = self.game_engine.get_city_summary()
        
        status_text = (
            f"Turn: {summary['turn']} | "
            f"💰 ${summary['money']:,.0f} | "
            f"👥 Pop: {summary['population']:,} | "
            f"😊 Satisfaction: {summary['satisfaction']:.1f}% | "
            f"📈 Unemployment: {summary['unemployment_rate']:.1f}%"
        )
        
        self.status_bar.showMessage(status_text)

    def on_tax_slider_changed(self, tax_key, value):
        """Obsługuje zmianę podatku przez slider"""
        self.game_engine.economy.tax_rates[tax_key] = value
        # Natychmiast odśwież panel ekonomii
        buildings = self.game_engine.get_all_buildings()
        income = self.game_engine.economy.calculate_taxes(buildings, self.game_engine.population)
        expenses = self.game_engine.economy.calculate_expenses(buildings, self.game_engine.population)
        tax_rates = self.game_engine.economy.tax_rates
        self.build_panel.update_economy_panel(income, expenses, tax_rates)
        self.update_status_bar()

    def on_building_sell_requested(self, x, y, building):
        """Obsługuje sprzedaż budynku po PPM na mapie"""
        success = self.game_engine.remove_building(x, y)
        if success:
            self.build_panel.update_resources(self.game_engine.economy)
            self.map_canvas.resources = self.game_engine.economy.get_resource_amount('money')
            self.update_status_bar()
            # Przelicz koszty i dochody po usunięciu budynku
            buildings = self.game_engine.get_all_buildings()
            income = self.game_engine.economy.calculate_taxes(buildings, self.game_engine.population)
            expenses = self.game_engine.economy.calculate_expenses(buildings, self.game_engine.population)
            tax_rates = self.game_engine.economy.tax_rates
            self.build_panel.update_economy_panel(income, expenses, tax_rates)
            self.map_canvas.draw_map()

    def on_building_sell_button(self):
        """Obsługuje sprzedaż budynku po kliknięciu przycisku w panelu"""
        tile = self.map_canvas.city_map.get_selected_tile()
        if tile and tile.building:
            x, y = tile.x, tile.y
            self.on_building_sell_requested(x, y, tile.building)

    def show_reports(self):
        self.reports_panel.show()

    def show_technology(self):
        self.technology_panel.show()

    def show_objectives(self):
        self.objectives_panel.show()
    
    def show_trade(self):
        """Show trade panel"""
        if not hasattr(self, 'trade_panel'):
            from gui.trade_panel import TradePanel
            self.trade_panel = TradePanel(self.game_engine)
            
            # Connect signals
            self.trade_panel.offer_accepted.connect(self.on_trade_offer_accepted)
            self.trade_panel.contract_created.connect(self.on_trade_contract_created)
        
        self.trade_panel.refresh_data()
        self.trade_panel.show()
    
    def show_achievements(self):
        """Show achievements panel"""
        if not hasattr(self, 'achievements_panel'):
            from gui.achievements_panel import AchievementsPanel
            self.achievements_panel = AchievementsPanel(self.game_engine)
        
        self.achievements_panel.refresh_data()
        self.achievements_panel.show()
    
    def on_trade_offer_accepted(self, offer_id):
        """Handle trade offer acceptance"""
        success, message = self.game_engine.accept_trade_offer(offer_id)
        if success:
            # Update resources after trade
            self.build_panel.update_resources(self.game_engine.economy)
            self.update_status_bar()
            QMessageBox.information(self, "Handel", f"Oferta handlowa zaakceptowana!\n{message}")
        else:
            QMessageBox.warning(self, "Handel", f"Nie można zaakceptować oferty:\n{message}")
    
    def on_trade_contract_created(self, city_id, good_type, quantity, price, duration, is_buying):
        """Handle trade contract creation"""
        success, message = self.game_engine.create_trade_contract(
            city_id, good_type, quantity, price, duration, is_buying
        )
        if success:
            # Update resources after contract creation
            self.build_panel.update_resources(self.game_engine.economy)
            self.update_status_bar()
            QMessageBox.information(self, "Handel", f"Kontrakt handlowy utworzony!\n{message}")
        else:
            QMessageBox.warning(self, "Handel", f"Nie można utworzyć kontraktu:\n{message}")
    
    def on_objective_completed(self, obj_id):
        """Handle objective completion"""
        objective = self.objective_manager.objectives.get(obj_id)
        if objective:
            # Apply rewards
            if objective.reward_money > 0:
                self.game_engine.economy.earn_money(objective.reward_money)
                self.build_panel.update_resources(self.game_engine.economy)
                
            if objective.reward_satisfaction > 0:
                # Apply satisfaction bonus to all population groups
                for group in self.game_engine.population.groups.values():
                    group.satisfaction = min(100, group.satisfaction + objective.reward_satisfaction)
            
            # Show completion message
            reward_text = []
            if objective.reward_money > 0:
                reward_text.append(f"${objective.reward_money:,}")
            if objective.reward_satisfaction > 0:
                reward_text.append(f"+{objective.reward_satisfaction} zadowolenia")
            
            reward_str = " i ".join(reward_text) if reward_text else "brak nagród"
            
            QMessageBox.information(
                self, 
                "Cel ukończony!", 
                f"🎉 Gratulacje!\n\n"
                f"Ukończono cel: {objective.title}\n"
                f"Nagroda: {reward_str}\n\n"
                f"{objective.reward_description}"
            )
            
            self.update_status_bar()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
