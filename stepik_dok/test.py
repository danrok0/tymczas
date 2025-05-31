import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try importing the module
try:
    from html_processor.utils.logger import log_info, log_error
    print("Successfully imported logger!")
except ImportError as e:
    print(f"Import failed: {e}")
    print(f"Python path: {sys.path}")
