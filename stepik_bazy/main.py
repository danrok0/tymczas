import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database_manager import DatabaseManager
from src.ui import UserInterface

def main():
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    db_manager.add_sample_data()
    
    # Create and run UI
    ui = UserInterface(db_manager)
    ui.run()

if __name__ == "__main__":
    main() 