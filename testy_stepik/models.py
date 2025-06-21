class Route:
    def __init__(self, name, distance, difficulty, terrain):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string")
        if not isinstance(distance, (int, float)) or distance < 0:
            raise ValueError("Distance must be a non-negative number")
        if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
            raise ValueError("Difficulty must be an integer between 1 and 5")
        if not isinstance(terrain, str) or not terrain.strip():
            raise ValueError("Terrain must be a non-empty string")
        
        self.name = name
        self.distance = distance
        self.difficulty = difficulty
        self.terrain = terrain
    
    def __eq__(self, other):
        if not isinstance(other, Route):
            return False
        return (self.name == other.name and 
                self.distance == other.distance and 
                self.difficulty == other.difficulty and 
                self.terrain == other.terrain)
    
    def __repr__(self):
        return f"Route(name='{self.name}', distance={self.distance}, difficulty={self.difficulty}, terrain='{self.terrain}')"


class UserPreference:
    def __init__(self, max_difficulty=None, terrain=None, max_distance=None):
        if max_difficulty is not None:
            if not isinstance(max_difficulty, int) or max_difficulty < 1 or max_difficulty > 5:
                raise ValueError("Max difficulty must be an integer between 1 and 5")
        if terrain is not None:
            if not isinstance(terrain, str) or not terrain.strip():
                raise ValueError("Terrain must be a non-empty string")
        if max_distance is not None:
            if not isinstance(max_distance, (int, float)) or max_distance < 0:
                raise ValueError("Max distance must be a non-negative number")
        
        self.max_difficulty = max_difficulty
        self.terrain = terrain
        self.max_distance = max_distance
    
    def __repr__(self):
        return f"UserPreference(max_difficulty={self.max_difficulty}, terrain='{self.terrain}', max_distance={self.max_distance})" 