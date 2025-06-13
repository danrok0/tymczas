from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QScrollArea, QGridLayout, QSlider, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor
from core.tile import Building, BuildingType
import os

class BuildPanel(QWidget):
    building_selected = pyqtSignal(Building)
    clear_selection = pyqtSignal()  # Nowy sygnał dla czyszczenia wyboru
    sell_building_clicked = pyqtSignal()  # Nowy sygnał do sprzedaży budynku
    
    def __init__(self, game_engine=None):
        super().__init__()
        self.game_engine = game_engine
        self.setMinimumWidth(360)  # Zwiększone z 320 dla szerszych przycisków
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                padding: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #4a6b8a;
            }
            QPushButton:checked {
                background-color: #2980b9;
            }
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Add title
        title = QLabel("Buildings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Add city level info section
        self.city_level_frame = QWidget()
        city_level_layout = QVBoxLayout(self.city_level_frame)
        
        self.city_level_title = QLabel("<b>Poziom miasta</b>")
        self.city_level_title.setStyleSheet("font-size: 14px; margin: 5px;")
        
        # Dodaj tooltip z wszystkimi progami poziomów
        level_thresholds_tooltip = (
            "Progi poziomów miasta:\n\n"
            "Poziom 1: 0 mieszkańców (start)\n"
            "Poziom 2: 600 mieszkańców\n"
            "Poziom 3: 1,400 mieszkańców\n"
            "Poziom 4: 2,800 mieszkańców\n"
            "Poziom 5: 5,000 mieszkańców\n"
            "Poziom 6: 8,000 mieszkańców\n"
            "Poziom 7: 12,000 mieszkańców\n"
            "Poziom 8: 17,000 mieszkańców\n"
            "Poziom 9: 23,000 mieszkańców\n"
            "Poziom 10: 30,000 mieszkańców\n\n"
            "💡 Każdy poziom odblokowuje nowe budynki!"
        )
        self.city_level_title.setToolTip(level_thresholds_tooltip)
        
        city_level_layout.addWidget(self.city_level_title)
        
        self.city_level_info = QLabel("Poziom: 1")
        self.city_level_info.setStyleSheet("font-size: 12px; margin: 2px;")
        city_level_layout.addWidget(self.city_level_info)
        
        self.next_level_info = QLabel("Do następnego poziomu: 0/600 mieszkańców")
        self.next_level_info.setStyleSheet("font-size: 12px; margin: 2px;")
        city_level_layout.addWidget(self.next_level_info)
        
        self.available_buildings_info = QLabel("Dostępne budynki: Podstawowe")
        self.available_buildings_info.setStyleSheet("font-size: 12px; margin: 2px;")
        city_level_layout.addWidget(self.available_buildings_info)
        
        layout.addWidget(self.city_level_frame)
        
        # Create scroll area for building buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create container for building buttons
        container = QWidget()
        container_layout = QGridLayout(container)
        
        # Define available buildings with expanded list (20+ buildings in 5 categories)
        self.buildings = [
            # Infrastruktura (Kategoria 1)
            Building("Droga", BuildingType.ROAD, 100, {"traffic": 2}),
            Building("Zakret drogi", BuildingType.ROAD_CURVE, 100, {"traffic": 2}, unlock_condition={"city_level": 2}),
            Building("Chodnik", BuildingType.SIDEWALK, 50, {"walkability": 3}, unlock_condition={"city_level": 2}),
            
            # Mieszkalne (Kategoria 2)
            Building("Dom", BuildingType.HOUSE, 500, {"population": 35, "happiness": 12}),
            Building("Blok", BuildingType.RESIDENTIAL, 800, {"population": 70, "happiness": 10}, unlock_condition={"city_level": 3}),
            Building("Wieżowiec", BuildingType.APARTMENT, 1500, {"population": 150, "happiness": 7}, unlock_condition={"city_level": 6}),
            
            # Komercyjne (Kategoria 3)
            Building("Sklep", BuildingType.SHOP, 800, {"commerce": 20, "jobs": 12}),
            Building("Targowisko", BuildingType.COMMERCIAL, 1200, {"commerce": 35, "jobs": 20}, unlock_condition={"city_level": 3}),
            Building("Centrum handlowe", BuildingType.MALL, 2000, {"commerce": 60, "jobs": 40}, unlock_condition={"city_level": 5}),
            
            # Przemysłowe (Kategoria 4)
            Building("Fabryka", BuildingType.FACTORY, 1500, {"production": 40, "jobs": 35, "pollution": -5}, unlock_condition={"city_level": 4}),
            Building("Magazyn", BuildingType.WAREHOUSE, 1000, {"storage": 30, "jobs": 15}, unlock_condition={"city_level": 3}),
            Building("Elektrownia", BuildingType.POWER_PLANT, 3000, {"energy": 150, "jobs": 20, "pollution": -10}, unlock_condition={"city_level": 4}),
            
            # Usługi publiczne (Kategoria 5)
            Building("Ratusz", BuildingType.CITY_HALL, 2500, {"administration": 40, "happiness": 15}, unlock_condition={"city_level": 2}),
            Building("Szkoła", BuildingType.SCHOOL, 1500, {"education": 30, "jobs": 20, "happiness": 10}, unlock_condition={"city_level": 3}),
            Building("Szpital", BuildingType.HOSPITAL, 2000, {"health": 35, "jobs": 25, "happiness": 12}, unlock_condition={"city_level": 5}),
            Building("Uniwersytet", BuildingType.UNIVERSITY, 3000, {"education": 50, "jobs": 40, "happiness": 15}, unlock_condition={"city_level": 7}),
            Building("Policja", BuildingType.POLICE, 1800, {"safety": 35, "jobs": 15, "happiness": 8}, unlock_condition={"city_level": 4}),
            Building("Straż Pożarna", BuildingType.FIRE_STATION, 1600, {"safety": 30, "jobs": 12, "happiness": 6}, unlock_condition={"city_level": 4}),
            Building("Park", BuildingType.PARK, 800, {"happiness": 20, "environment": 15}, unlock_condition={"city_level": 2}),
            Building("Stadion", BuildingType.STADIUM, 4000, {"happiness": 40, "tourism": 30, "jobs": 35}, unlock_condition={"city_level": 8}),
            Building("Oczyszczalnia wody", BuildingType.WATER_TREATMENT, 2200, {"water": 70, "jobs": 12}, unlock_condition={"city_level": 5})
        ]
        
        # Create building buttons
        self.building_buttons = []
        for i, building in enumerate(self.buildings):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(160, 110)  # Zwiększone szerokość z 145 na 160
            
            # Try to load building icon
            icon_path = building.get_image_path()
            if icon_path:
                # Try to load from absolute path
                abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), icon_path)
                pixmap = QPixmap(abs_path)
                if not pixmap.isNull():
                    # Scale icon to fit button
                    scaled_pixmap = pixmap.scaled(75, 75, Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation)
                    btn.setIcon(QIcon(scaled_pixmap))
                    btn.setIconSize(scaled_pixmap.size())
                else:
                    # If image fails to load, create colored icon
                    self._create_color_icon(btn, building)
            else:
                # Create colored icon for buildings without images
                self._create_color_icon(btn, building)
            
            # Set building name as tooltip with effects
            effects_str = ", ".join([f"{k}: +{v}" for k, v in building.effects.items()])
            unlock_info = ""
            is_unlocked = True
            if self.game_engine and hasattr(self.game_engine, 'is_building_unlocked'):
                is_unlocked, reason = self.game_engine.is_building_unlocked(building)
                # Now always show clear unlock info
                unlock_details = []
                if hasattr(building, 'unlock_condition') and building.unlock_condition:
                    if 'city_level' in building.unlock_condition:
                        unlock_details.append(f"Od poziomu miasta: {building.unlock_condition['city_level']}")
                    if 'population' in building.unlock_condition:
                        unlock_details.append(f"Wymagana populacja: {building.unlock_condition['population']}")
                if unlock_details:
                    unlock_info = "\n\n" + " | ".join(unlock_details)
                elif not is_unlocked:
                    unlock_info = f"\n\n🔒 Zablokowane: {reason}"
                else:
                    unlock_info = "\n\nDostępny od początku gry"
            btn.setToolTip(f"{building.name}\nCost: ${building.cost:,}\nEffects: {effects_str}{unlock_info}")
            btn.setEnabled(is_unlocked)
            
            # Add building name text with better formatting for wider buttons
            name = building.name
            if len(name) > 15:  # Zwiększone z 13 dla szerszych przycisków
                # Break long names into two lines
                words = name.split()
                if len(words) > 1:
                    mid = len(words) // 2
                    line1 = " ".join(words[:mid])
                    line2 = " ".join(words[mid:])
                    name = f"{line1}\n{line2}"
                else:
                    # Single long word - truncate
                    if len(name) > 18:  # Zwiększone z 16
                        name = name[:15] + "..."
            
            btn.setText(name)
            
            # Style for better text display in 2-column layout
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    border: 1px solid #2c3e50;
                    padding: 7px 5px;
                    margin: 2px;
                    font-size: 11px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #4a6b8a;
                }
                QPushButton:checked {
                    background-color: #2980b9;
                }
            """)
            
            # Connect click event
            btn.clicked.connect(lambda checked, b=building: self.on_building_selected(b))
            
            # Add to layout - 2 columns
            row = i // 2
            col = i % 2
            container_layout.addWidget(btn, row, col)
            self.building_buttons.append(btn)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Add clear selection button
        self.clear_btn = QPushButton("Wyczyść wybór")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: 1px solid #c0392b;
                padding: 8px;
                margin: 2px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.clear_btn)
        
        # Connect clear button
        self.clear_btn.clicked.connect(self.on_clear_selection)
        
        # Add sell building button
        self.sell_btn = QPushButton("Sprzedaj budynek (wybrany na mapie)")
        self.sell_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                border: 1px solid #145a32;
                padding: 8px;
                margin: 2px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #145a32;
            }
        """)
        layout.addWidget(self.sell_btn)
        self.sell_btn.clicked.connect(self.sell_building_clicked.emit)
        
        # Add rotate button
        self.rotate_btn = QPushButton("Rotate (R)")
        self.rotate_btn.setEnabled(False)
        layout.addWidget(self.rotate_btn)
        
        # --- Sekcja: Zasoby miasta ---
        self.resources_title = QLabel("<b>Zasoby miasta</b>")
        self.resources_title.setStyleSheet("margin-top: 10px; font-size: 14px;")
        layout.addWidget(self.resources_title)
        
        # Podstawowe zasoby
        self.money_label = QLabel("💰 Pieniądze: $50,000")
        self.energy_label = QLabel("⚡ Energia: 100/1000")
        self.water_label = QLabel("💧 Woda: 100/1000")
        self.materials_label = QLabel("🔨 Materiały: 50/500")
        self.food_label = QLabel("🍞 Żywność: 80/800")
        self.luxury_label = QLabel("💎 Towary luksusowe: 20/200")
        
        # Dodaj tooltips
        self.money_label.setToolTip("Główna waluta miasta - używana do budowy i utrzymania")
        self.energy_label.setToolTip("Energia potrzebna do zasilania budynków")
        self.water_label.setToolTip("Woda potrzebna mieszkańcom i przemysłowi")
        self.materials_label.setToolTip("Materiały budowlane do konstrukcji")
        self.food_label.setToolTip("Żywność dla mieszkańców")
        self.luxury_label.setToolTip("Towary luksusowe zwiększające zadowolenie")
        
        layout.addWidget(self.money_label)
        layout.addWidget(self.energy_label)
        layout.addWidget(self.water_label)
        layout.addWidget(self.materials_label)
        layout.addWidget(self.food_label)
        layout.addWidget(self.luxury_label)

        # --- Nowa sekcja: Ekonomia miasta ---
        self.economy_title = QLabel("<b>Ekonomia miasta</b>")
        self.economy_title.setStyleSheet("margin-top: 10px; font-size: 14px;")
        layout.addWidget(self.economy_title)

        self.income_label = QLabel("📈 Dochód/turę: $0")
        self.expenses_label = QLabel("📉 Wydatki/turę: $0")
        self.tax_label = QLabel("🏛️ Podatki: 5% / 8% / 10%")
        self.income_label.setToolTip("Suma podatków i przychodów z budynków na turę")
        self.expenses_label.setToolTip("Suma kosztów utrzymania budynków na turę")
        self.tax_label.setToolTip("Stawki podatkowe: mieszkaniowe / komercyjne / przemysłowe")
        layout.addWidget(self.income_label)
        layout.addWidget(self.expenses_label)
        layout.addWidget(self.tax_label)
        
        # --- Slidery do zmiany podatków ---
        self.tax_sliders = {}
        self.tax_slider_labels = {}
        tax_types = [('residential', 'Mieszkaniowy', 5), ('commercial', 'Komercyjny', 8), ('industrial', 'Przemysłowy', 10)]
        for tax_key, tax_name, default_value in tax_types:
            hbox = QHBoxLayout()
            label = QLabel(f"{tax_name}: ")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(20)
            slider.setValue(default_value)
            slider.setTickInterval(1)
            slider.setSingleStep(1)
            slider.setToolTip(f"Stawka podatku {tax_name.lower()} (%)")
            value_label = QLabel(f"{slider.value()}%")
            slider.valueChanged.connect(lambda val, k=tax_key, l=value_label: self._on_tax_slider_changed(k, val, l))
            hbox.addWidget(label)
            hbox.addWidget(slider)
            hbox.addWidget(value_label)
            layout.addLayout(hbox)
            self.tax_sliders[tax_key] = slider
            self.tax_slider_labels[tax_key] = value_label

        # Add status label
        self.status_label = QLabel("Select a building to place")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def on_building_selected(self, building: Building):
        """Handles building selection"""
        # Uncheck all other buttons
        for btn in self.building_buttons:
            btn.setChecked(btn.toolTip().startswith(building.name))
        
        # Enable rotate button for all buildings now
        self.rotate_btn.setEnabled(True)  # Wszystkie budynki można teraz obracać
        
        # Emit signal
        self.building_selected.emit(building)
    
    def on_clear_selection(self):
        """Handles clearing building selection"""
        # Uncheck all buttons
        for btn in self.building_buttons:
            btn.setChecked(False)
        
        # Disable rotate button
        self.rotate_btn.setEnabled(False)
        
        # Emit clear signal
        self.clear_selection.emit()
        
        # Update status
        self.update_status("No building selected")
    
    def update_resources(self, economy):
        """Updates all resources display"""
        if hasattr(economy, 'get_resource_amount'):
            # Aktualizuj wszystkie zasoby
            money = economy.get_resource_amount('money')
            energy = economy.get_resource_amount('energy')
            water = economy.get_resource_amount('water')
            materials = economy.get_resource_amount('materials')
            food = economy.get_resource_amount('food')
            luxury = economy.get_resource_amount('luxury_goods')
            
            # Pobierz maksymalne pojemności
            energy_max = economy.get_resource('energy').max_capacity
            water_max = economy.get_resource('water').max_capacity
            materials_max = economy.get_resource('materials').max_capacity
            food_max = economy.get_resource('food').max_capacity
            luxury_max = economy.get_resource('luxury_goods').max_capacity
            
            # Aktualizuj etykiety
            self.money_label.setText(f"💰 Pieniądze: ${money:,.0f}")
            self.energy_label.setText(f"⚡ Energia: {energy:.0f}/{energy_max:.0f}")
            self.water_label.setText(f"💧 Woda: {water:.0f}/{water_max:.0f}")
            self.materials_label.setText(f"🔨 Materiały: {materials:.0f}/{materials_max:.0f}")
            self.food_label.setText(f"🍞 Żywność: {food:.0f}/{food_max:.0f}")
            self.luxury_label.setText(f"💎 Towary luksusowe: {luxury:.0f}/{luxury_max:.0f}")
        else:
            # Fallback dla starych wywołań z samą kwotą pieniędzy
            self.money_label.setText(f"💰 Pieniądze: ${economy:,.0f}")

    def update_status(self, message: str):
        """Updates the status message"""
        self.status_label.setText(message)

    def _create_color_icon(self, button: QPushButton, building: Building):
        """Creates a colored icon for buildings without images"""
        # Create a colored pixmap
        pixmap = QPixmap(75, 75)  # Zwiększone z 70x70
        color = QColor(building.get_color())
        pixmap.fill(color)

        # Add border
        painter = QPainter(pixmap)
        painter.setPen(QColor("#000000"))
        painter.drawRect(0, 0, 74, 74)  # Adjusted for new size
        painter.end()

        button.setIcon(QIcon(pixmap))
        button.setIconSize(pixmap.size())

    def update_economy_panel(self, income, expenses, tax_rates):
        """Aktualizuje panel ekonomii miasta"""
        self.income_label.setText(f"📈 Dochód/turę: ${income:,.0f}")
        self.expenses_label.setText(f"📉 Wydatki/turę: ${expenses:,.0f}")
        self.tax_label.setText(f"🏛️ Podatki: {tax_rates['residential']*100:.0f}% / {tax_rates['commercial']*100:.0f}% / {tax_rates['industrial']*100:.0f}%")

    def _on_tax_slider_changed(self, tax_key, value, value_label):
        value_label.setText(f"{value}%")
        self.parent().parent().on_tax_slider_changed(tax_key, value/100)

    def refresh_building_availability(self):
        """Refreshes the availability status of all building buttons"""
        if not self.game_engine:
            return

        for btn, building in zip(self.building_buttons, self.buildings):
            is_unlocked, reason = self.game_engine.is_building_unlocked(building)
            btn.setEnabled(is_unlocked)
            
            # Update tooltip with current unlock status
            effects_str = ", ".join([f"{k}: +{v}" for k, v in building.effects.items()])
            unlock_info = f"\n\n🔒 Zablokowane: {reason}" if not is_unlocked else ""
            btn.setToolTip(f"{building.name}\nCost: ${building.cost:,}\nEffects: {effects_str}{unlock_info}")

    def update_city_level_info(self, level: int, current_pop: int, next_level_pop: int):
        """Updates the city level information display"""
        self.city_level_info.setText(f"Poziom: {level}")
        
        # Calculate progress to next level
        if next_level_pop > 0:
            progress = current_pop / next_level_pop * 100
            progress_text = f"Do następnego poziomu: {current_pop:,}/{next_level_pop:,} mieszkańców ({progress:.1f}%)"
            self.next_level_info.setText(progress_text)
            
            # Dodaj tooltip z wyjaśnieniem
            tooltip_text = (
                f"Aktualny poziom miasta: {level}\n"
                f"Następny poziom: {level + 1}\n"
                f"Wymagana populacja: {next_level_pop:,}\n"
                f"Aktualna populacja: {current_pop:,}\n"
                f"Postęp: {progress:.1f}%\n\n"
                "💡 Próg może się zmienić po awansie na wyższy poziom"
            )
            self.next_level_info.setToolTip(tooltip_text)
        else:
            # Maksymalny poziom osiągnięty
            self.next_level_info.setText(f"Maksymalny poziom osiągnięty! Populacja: {current_pop:,}")
            self.next_level_info.setToolTip("Osiągnąłeś najwyższy poziom miasta!")
        
        # Update available buildings info based on actual unlock conditions
        available_buildings = self._get_available_buildings_for_level(level)
        next_level_preview = self._get_next_level_preview(level)
        
        buildings_text = f"Dostępne budynki: {available_buildings}"
        if next_level_preview:
            buildings_text += f"\n\nNa poziomie {level + 1}: {next_level_preview}"
        
        self.available_buildings_info.setText(buildings_text)
    
    def _get_available_buildings_for_level(self, level: int) -> str:
        """Returns a description of buildings available at the given level"""
        # Always available (no unlock condition or level 1)
        always_available = ["Dom", "Sklep", "Droga"]
        
        # Buildings by level
        level_buildings = {
            2: ["Zakret drogi", "Chodnik", "Ratusz", "Park"],
            3: ["Blok", "Targowisko", "Magazyn", "Szkoła"],
            4: ["Fabryka", "Elektrownia", "Policja", "Straż Pożarna"],
            5: ["Centrum handlowe", "Szpital", "Oczyszczalnia wody"],
            6: ["Wieżowiec"],
            7: ["Uniwersytet"],
            8: ["Stadion"]
        }
        
        # Collect all available buildings up to current level
        available = always_available.copy()
        for lvl in range(2, level + 1):
            if lvl in level_buildings:
                available.extend(level_buildings[lvl])
        
        # Create description based on level
        if level == 1:
            return "Podstawowe (Dom, Sklep, Droga)"
        elif level == 2:
            new_buildings = level_buildings.get(2, [])
            return f"Podstawowe + {', '.join(new_buildings)}"
        elif level == 3:
            new_buildings = level_buildings.get(3, [])
            return f"Poprzednie + {', '.join(new_buildings)}"
        elif level == 4:
            new_buildings = level_buildings.get(4, [])
            return f"Poprzednie + {', '.join(new_buildings)}"
        elif level == 5:
            new_buildings = level_buildings.get(5, [])
            return f"Poprzednie + {', '.join(new_buildings)}"
        elif level == 6:
            new_buildings = level_buildings.get(6, [])
            return f"Poprzednie + {', '.join(new_buildings)}"
        elif level == 7:
            new_buildings = level_buildings.get(7, [])
            return f"Poprzednie + {', '.join(new_buildings)}"
        elif level >= 8:
            if level == 8:
                new_buildings = level_buildings.get(8, [])
                return f"Poprzednie + {', '.join(new_buildings)} (Wszystkie budynki)"
            else:
                return "Wszystkie budynki dostępne"
        
        return "Podstawowe"
    
    def _get_next_level_preview(self, current_level: int) -> str:
        """Returns a preview of buildings that will be unlocked at the next level"""
        level_buildings = {
            2: ["Zakret drogi", "Chodnik", "Ratusz", "Park"],
            3: ["Blok", "Targowisko", "Magazyn", "Szkoła"],
            4: ["Fabryka", "Elektrownia", "Policja", "Straż Pożarna"],
            5: ["Centrum handlowe", "Szpital", "Oczyszczalnia wody"],
            6: ["Wieżowiec"],
            7: ["Uniwersytet"],
            8: ["Stadion"]
        }
        
        next_level = current_level + 1
        if next_level in level_buildings:
            buildings = level_buildings[next_level]
            return f"Odblokuje się: {', '.join(buildings)}"
        elif next_level > 8:
            return ""
        else:
            return "Brak nowych budynków"

