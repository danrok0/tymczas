from models import UserPreference


class RouteRecommender:
    def __init__(self, repository):
        self.repository = repository
    
    def recommend(self, user_preference):
        if not isinstance(user_preference, UserPreference):
            raise ValueError("user_preference must be an instance of UserPreference")
        
        all_routes = self.repository.get_all()
        filtered_routes = []
        
        for route in all_routes:
            # Check difficulty constraint
            if (user_preference.max_difficulty is not None and 
                route.difficulty > user_preference.max_difficulty):
                continue
            
            # Check terrain constraint
            if (user_preference.terrain is not None and 
                route.terrain != user_preference.terrain):
                continue
            
            # Check distance constraint
            if (user_preference.max_distance is not None and 
                route.distance > user_preference.max_distance):
                continue
            
            filtered_routes.append(route)
        
        return filtered_routes 