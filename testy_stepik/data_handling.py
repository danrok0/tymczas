import csv
import os
from models import Route


class DataParsingError(Exception):
    """Wyjątek rzucany gdy wystąpi błąd podczas parsowania danych"""
    pass


class FileRouteRepository:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def get_all(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        routes = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row_num, row in enumerate(reader, start=2):  # start=2 because first row is header
                    try:
                        name = row['name']
                        distance = float(row['distance'])
                        difficulty = int(row['difficulty'])
                        terrain = row['terrain']
                        
                        route = Route(name, distance, difficulty, terrain)
                        routes.append(route)
                    except (ValueError, KeyError) as e:
                        raise DataParsingError(f"Error parsing row {row_num}: {str(e)}")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, DataParsingError)):
                raise
            raise DataParsingError(f"Error reading file: {str(e)}")
        
        return routes 