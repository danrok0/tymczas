from datetime import datetime

def log_info(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO] {message}")

def log_error(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ERROR] {message}")