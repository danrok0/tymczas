import matplotlib
matplotlib.use('Qt5Agg')  # Ustaw backend przed importem pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
import csv
import os
from datetime import datetime

class ReportsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_data = {
            'turns': [],
            'population': [],
            'budget': [],
            'satisfaction': [],
            'unemployment': [],
            'income': [],
            'expenses': []
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Control panel
        controls_layout = QHBoxLayout()
        
        # Time range selector
        controls_layout.addWidget(QLabel("Zakres czasu:"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["Ostatnie 10 tur", "Ostatnie 25 tur", "Ostatnie 50 tur", "Wszystkie dane"])
        self.time_range_combo.currentTextChanged.connect(self.update_charts)
        controls_layout.addWidget(self.time_range_combo)
        
        # Export button
        self.export_btn = QPushButton("Eksportuj do CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        controls_layout.addWidget(self.export_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Odśwież")
        self.refresh_btn.clicked.connect(self.update_charts)
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)

        # Create figure and canvas
        self.figure = plt.figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Create subplots with better layout
        self.ax1 = self.figure.add_subplot(231)  # 2x3 grid
        self.ax2 = self.figure.add_subplot(232)
        self.ax3 = self.figure.add_subplot(233)
        self.ax4 = self.figure.add_subplot(234)
        self.ax5 = self.figure.add_subplot(235)
        self.ax6 = self.figure.add_subplot(236)

        self.setLayout(layout)
        self.setWindowTitle("Raporty i Statystyki Miasta")
        self.resize(1000, 700)

    def add_data_point(self, turn, population, budget, satisfaction, unemployment, income, expenses):
        """Dodaje nowy punkt danych do historii"""
        self.history_data['turns'].append(turn)
        self.history_data['population'].append(population)
        self.history_data['budget'].append(budget)
        self.history_data['satisfaction'].append(satisfaction)
        self.history_data['unemployment'].append(unemployment)
        self.history_data['income'].append(income)
        self.history_data['expenses'].append(expenses)
        
        # Ograniczenie do ostatnich 200 punktów dla wydajności
        max_points = 200
        for key in self.history_data:
            if len(self.history_data[key]) > max_points:
                self.history_data[key] = self.history_data[key][-max_points:]

    def get_filtered_data(self):
        """Zwraca dane przefiltrowane według wybranego zakresu"""
        range_text = self.time_range_combo.currentText()
        
        if range_text == "Ostatnie 10 tur":
            limit = 10
        elif range_text == "Ostatnie 25 tur":
            limit = 25
        elif range_text == "Ostatnie 50 tur":
            limit = 50
        else:
            limit = len(self.history_data['turns'])
        
        filtered_data = {}
        for key, values in self.history_data.items():
            filtered_data[key] = values[-limit:] if len(values) > limit else values
        
        return filtered_data

    def update_charts(self):
        """Aktualizuje wszystkie wykresy"""
        data = self.get_filtered_data()
        
        if not data['turns']:
            return
        
        # Clear previous plots
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
            ax.clear()

        turns = data['turns']

        # 1. Populacja
        self.ax1.plot(turns, data['population'], 'b-', linewidth=2, marker='o', markersize=4)
        self.ax1.set_title('Populacja', fontsize=12, fontweight='bold')
        self.ax1.set_ylabel('Mieszkańcy')
        self.ax1.grid(True, alpha=0.3)

        # 2. Budżet
        self.ax2.plot(turns, data['budget'], 'g-', linewidth=2, marker='s', markersize=4)
        self.ax2.set_title('Budżet Miasta', fontsize=12, fontweight='bold')
        self.ax2.set_ylabel('Pieniądze ($)')
        self.ax2.grid(True, alpha=0.3)

        # 3. Zadowolenie
        self.ax3.plot(turns, data['satisfaction'], 'orange', linewidth=2, marker='^', markersize=4)
        self.ax3.set_title('Zadowolenie Mieszkańców', fontsize=12, fontweight='bold')
        self.ax3.set_ylabel('Zadowolenie (%)')
        self.ax3.set_ylim(0, 100)
        self.ax3.grid(True, alpha=0.3)

        # 4. Bezrobocie
        self.ax4.plot(turns, data['unemployment'], 'r-', linewidth=2, marker='v', markersize=4)
        self.ax4.set_title('Stopa Bezrobocia', fontsize=12, fontweight='bold')
        self.ax4.set_ylabel('Bezrobocie (%)')
        self.ax4.grid(True, alpha=0.3)

        # 5. Dochody vs Wydatki
        self.ax5.plot(turns, data['income'], 'g-', linewidth=2, label='Dochody', marker='o', markersize=3)
        self.ax5.plot(turns, data['expenses'], 'r-', linewidth=2, label='Wydatki', marker='s', markersize=3)
        self.ax5.set_title('Ekonomia - Dochody vs Wydatki', fontsize=12, fontweight='bold')
        self.ax5.set_ylabel('Pieniądze ($)')
        self.ax5.legend()
        self.ax5.grid(True, alpha=0.3)

        # 6. Bilans (Dochody - Wydatki)
        if len(data['income']) == len(data['expenses']):
            balance = [inc - exp for inc, exp in zip(data['income'], data['expenses'])]
            colors = ['g' if b >= 0 else 'r' for b in balance]
            self.ax6.bar(turns, balance, color=colors, alpha=0.7)
            self.ax6.set_title('Bilans Budżetowy', fontsize=12, fontweight='bold')
            self.ax6.set_ylabel('Bilans ($)')
            self.ax6.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            self.ax6.grid(True, alpha=0.3)

        # Ustawienia osi X dla wszystkich wykresów
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
            ax.set_xlabel('Tura')

        # Adjust layout and redraw
        self.figure.tight_layout()
        self.canvas.draw()

    def export_to_csv(self):
        """Eksportuje dane do pliku CSV"""
        try:
            # Ensure exports directory exists
            export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(export_dir, f"city_report_{timestamp}.csv")
            
            # Write CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow(['Tura', 'Populacja', 'Budżet', 'Zadowolenie (%)', 
                               'Bezrobocie (%)', 'Dochody', 'Wydatki', 'Bilans'])
                
                # Data rows
                for i in range(len(self.history_data['turns'])):
                    income = self.history_data['income'][i] if i < len(self.history_data['income']) else 0
                    expenses = self.history_data['expenses'][i] if i < len(self.history_data['expenses']) else 0
                    balance = income - expenses
                    
                    writer.writerow([
                        self.history_data['turns'][i],
                        self.history_data['population'][i],
                        self.history_data['budget'][i],
                        round(self.history_data['satisfaction'][i], 1),
                        round(self.history_data['unemployment'][i], 1),
                        income,
                        expenses,
                        balance
                    ])
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, 'Eksport', f'Dane wyeksportowane do:\n{filename}')
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Błąd eksportu', f'Nie udało się wyeksportować danych:\n{str(e)}')

    def update_reports(self, population_history, budget_history, satisfaction_history, resources_history):
        """Zachowuje kompatybilność z poprzednią wersją (deprecated)"""
        # Ta metoda jest zachowana dla kompatybilności, ale zaleca się używanie add_data_point
        if population_history and budget_history and satisfaction_history:
            # Dodaj tylko ostatni punkt jeśli to nowe dane
            if not self.history_data['turns'] or len(population_history) > len(self.history_data['population']):
                turn = len(self.history_data['turns']) + 1
                self.add_data_point(
                    turn=turn,
                    population=population_history[-1] if population_history else 0,
                    budget=budget_history[-1] if budget_history else 0,
                    satisfaction=satisfaction_history[-1] if satisfaction_history else 0,
                    unemployment=0,  # Będzie aktualizowane przez add_data_point
                    income=0,  # Będzie aktualizowane przez add_data_point
                    expenses=0  # Będzie aktualizowane przez add_data_point
                )
                self.update_charts()
