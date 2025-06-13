from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class EventDialog(QDialog):
    def __init__(self, event, parent=None):
        super().__init__(parent)
        self.event = event
        self.selected_option = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.event.title)
        layout = QVBoxLayout()

        description_label = QLabel(self.event.description)
        layout.addWidget(description_label)

        options_layout = QHBoxLayout()
        for option in self.event.options:
            button = QPushButton(option)
            button.clicked.connect(lambda checked, opt=option: self.select_option(opt))
            options_layout.addWidget(button)

        layout.addLayout(options_layout)
        self.setLayout(layout)

    def select_option(self, option):
        self.selected_option = option
        self.accept() 