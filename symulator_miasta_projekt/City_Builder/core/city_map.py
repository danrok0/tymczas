import random
from .tile import Tile, TerrainType

class CityMap:
    def __init__(self, width: int = 50, height: int = 50):
        self.width = width
        self.height = height
        self.grid = self._create_grid()
        self.selected_tile = None
        
    def _create_grid(self) -> list[list[Tile]]:
        """Creates a 2D grid of tiles with random terrain"""
        grid = []
        
        # First, fill everything with grass
        for x in range(self.width):
            row = []
            for y in range(self.height):
                row.append(Tile(x, y, TerrainType.GRASS))
            grid.append(row)
        
        # Add natural features
        self._add_natural_features(grid)
        
        return grid
    
    def _add_natural_features(self, grid: list[list[Tile]]):
        """Adds natural features to the map"""
        # Add some water bodies
        self._add_terrain_clusters(grid, TerrainType.WATER, 5, 10, 0.7)
        
        # Add some mountains
        self._add_terrain_clusters(grid, TerrainType.MOUNTAIN, 3, 5, 0.6)
        
        # Add some sand areas
        self._add_terrain_clusters(grid, TerrainType.SAND, 4, 8, 0.5)
    
    def _add_terrain_clusters(self, grid: list[list[Tile]], terrain_type: TerrainType, 
                            num_clusters: int, max_size: int, spread_prob: float):
        """Adds clusters of a specific terrain type"""
        for _ in range(num_clusters):
            # Choose a random starting point
            start_x = random.randint(0, self.width - 1)
            start_y = random.randint(0, self.height - 1)
            
            # Create a cluster
            self._grow_cluster(grid, start_x, start_y, terrain_type, max_size, spread_prob)
    
    def _grow_cluster(self, grid: list[list[Tile]], x: int, y: int, 
                     terrain_type: TerrainType, max_size: int, spread_prob: float):
        """Grows a cluster of terrain from a starting point"""
        if max_size <= 0:
            return
            
        # Only change grass tiles
        if grid[x][y].terrain_type != TerrainType.GRASS:
            return
            
        # Change the tile
        grid[x][y] = Tile(x, y, terrain_type)
        
        # Try to spread in all directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and 
                random.random() < spread_prob):
                self._grow_cluster(grid, nx, ny, terrain_type, max_size - 1, spread_prob)
    
    def get_tile(self, x: int, y: int) -> Tile | None:
        """Returns tile at given coordinates or None if out of bounds"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None
    
    def select_tile(self, x: int, y: int) -> None:
        """Selects a tile at given coordinates"""
        tile = self.get_tile(x, y)
        if tile:
            self.selected_tile = tile
    
    def deselect_tile(self) -> None:
        """Deselects the currently selected tile"""
        self.selected_tile = None
            
    def get_selected_tile(self) -> Tile | None:
        """Returns currently selected tile"""
        return self.selected_tile
