import os
import time
import random
from copy import deepcopy
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QFrame
from PyQt6.QtCore import pyqtSignal, Qt, QRectF, QPointF, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QTransform, QImage, QIcon, QMouseEvent, QWheelEvent

from core.city_map import CityMap
from core.tile import Building, TerrainType

class MapCanvas(QGraphicsView):
    # Signal emitted when a tile is clicked
    tile_clicked = pyqtSignal(int, int)
    building_placed = pyqtSignal(int, int, Building)
    building_sell_requested = pyqtSignal(int, int, Building)
    
    def __init__(self, city_map: CityMap):
        super().__init__()
        self.city_map = city_map
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Set focus policy to receive keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()  # Ustaw focus na start
        
        # Building selection and rotation
        self.selected_building = None
        self.preview_rotation = 0  # Rotacja podglądu (nie modyfikuje oryginalnego budynku)
        self._last_rotate_time = 0  # Czas ostatniej rotacji
        
        # Hover tracking
        self.hover_tile_x = -1
        self.hover_tile_y = -1
        
        # Performance optimization
        self._last_update_time = 0
        
        # Display settings
        self.tile_size = 32
        self.zoom_factor = 1.0
        
        # Image cache and resources
        self.image_cache = {}
        self.resources = 0
        
        # Optimization for preview rendering
        self._last_hover_x = -1
        self._last_hover_y = -1
        self._preview_items = []  # Track preview items for removal
        self._cleanup_counter = 0  # Counter for periodic cleanup
        
        # Setup scrollbars and rendering
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Initial draw
        self.draw_map()
    
    def get_tile_image(self, tile_path: str) -> QPixmap:
        """Gets tile image from cache or loads it if not cached"""
        if tile_path not in self.image_cache:
            # Get absolute path
            abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), tile_path)
            
            # Load image with alpha channel support
            image = QImage(abs_path)
            if not image.isNull():
                # Convert to format that supports transparency
                if image.format() != QImage.Format.Format_ARGB32:
                    image = image.convertToFormat(QImage.Format.Format_ARGB32)
                
                # Create a new pixmap with transparency
                pixmap = QPixmap.fromImage(image)
                
                # Scale the image to fill the tile while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.tile_size, self.tile_size,
                                            Qt.AspectRatioMode.IgnoreAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                
                # Create a new pixmap with transparency
                final_pixmap = QPixmap(self.tile_size, self.tile_size)
                final_pixmap.fill(Qt.GlobalColor.transparent)
                
                # Create a painter to draw the scaled image
                painter = QPainter(final_pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                
                # Draw the scaled image
                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.end()
                
                self.image_cache[tile_path] = final_pixmap
            else:
                # If image loading fails, create a colored rectangle
                pixmap = QPixmap(self.tile_size, self.tile_size)
                pixmap.fill(QColor("#FF0000"))  # Red to indicate error
                self.image_cache[tile_path] = pixmap
        return self.image_cache[tile_path]
    
    def select_building(self, building: Building | None):
        """Selects a building for placement"""
        # Deselect any selected tile when selecting a building
        self.city_map.deselect_tile()
        
        self.selected_building = building
        self.preview_rotation = 0  # Resetuj rotację podglądu przy nowym budynku
        if building:
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.setFocus()  # Ustaw focus żeby klawisz R działał od razu
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
        # Natychmiastowe pełne przerysowanie
        self.draw_map()
    
    def rotate_building(self):
        """Rotates the preview of selected building"""
        if not self.selected_building:
            return
            
        current_time = time.time()
        
        # Limit rotation rate to prevent artifacts
        if current_time - self._last_rotate_time < 0.2:
            return
        
        self.preview_rotation = (self.preview_rotation + 90) % 360
        
        # Pełne przerysowanie zamiast inkrementalnej aktualizacji
        self.draw_map()
        
        self._last_rotate_time = current_time
    
    def can_build(self, x: int, y: int) -> bool:
        """Checks if a building can be placed at the given coordinates"""
        tile = self.city_map.get_tile(x, y)
        if not tile:
            return False
        
        if tile.is_occupied:
            return False
        
        # Check terrain compatibility - block building on water and mountains
        if tile.terrain_type in [TerrainType.WATER, TerrainType.MOUNTAIN]:
            return False
        
        # Check if we have enough resources
        if self.selected_building and self.resources < self.selected_building.cost:
            return False
        
        return True
    
    def place_building(self, x: int, y: int):
        """Places the selected building at the given coordinates"""
        if not self.selected_building:
            return
            
        if not self.can_build(x, y):
            return
        
        # Create a copy of the building to preserve its rotation state
        building_copy = deepcopy(self.selected_building)
        building_copy.rotation = self.preview_rotation  # Ustaw rotację z podglądu
        
        # Emit signal to let GameEngine handle the actual placement
        self.building_placed.emit(x, y, building_copy)

        # Natychmiastowe pełne przerysowanie
        self.draw_map()
    
    def draw_map(self):
        """Draws the city map with all tiles, buildings, and overlays"""
        # --- CAŁKOWITE CZYSZCZENIE PRZED RYSOWANIEM ---
        
        # Clear the scene completely and reset all items
        self.scene.clear()
        self._preview_items.clear()  # Reset preview tracking
        
        # Cache frequently used values
        tile_size = self.tile_size
        map_width = self.city_map.width
        map_height = self.city_map.height
        
        # Pre-calculate scene rect
        scene_width = map_width * tile_size
        scene_height = map_height * tile_size
        
        for x in range(map_width):
            for y in range(map_height):
                tile = self.city_map.get_tile(x, y)
                if not tile:
                    continue
                
                # Calculate position once
                pos_x = x * tile_size
                pos_y = y * tile_size
                rect = QRectF(pos_x, pos_y, tile_size, tile_size)
                
                # Draw terrain first (Z-level 0)
                terrain_image_path = tile.get_image_path()
                if terrain_image_path:
                    # Draw terrain image
                    terrain_pixmap = self.get_tile_image(terrain_image_path)
                    terrain_item = self.scene.addPixmap(terrain_pixmap)
                    terrain_item.setPos(pos_x, pos_y)
                    terrain_item.setZValue(0)
                else:
                    # Fallback to colored rectangle for terrain
                    terrain_color = tile.get_color()
                    terrain_brush = QBrush(QColor(terrain_color))
                    terrain_rect = self.scene.addRect(rect, QPen(Qt.GlobalColor.black, 1), terrain_brush)
                    terrain_rect.setZValue(0)
                
                # Draw building if present (Z-level 1)
                if tile.building:
                    building_path = tile.building.get_image_path()
                    if building_path:
                        # Try to load building image
                        building_pixmap = self.get_tile_image(building_path)
                        
                        # Apply rotation if building has rotation
                        if hasattr(tile.building, 'rotation') and tile.building.rotation != 0:
                            transform = QTransform()
                            transform.translate(tile_size/2, tile_size/2)
                            transform.rotate(tile.building.rotation)
                            transform.translate(-tile_size/2, -tile_size/2)
                            building_pixmap = building_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
                        
                        building_item = self.scene.addPixmap(building_pixmap)
                        building_item.setPos(pos_x, pos_y)
                        building_item.setZValue(1)
                    else:
                        # Fallback to colored rectangle
                        color = QColor(tile.building.get_color())
                        brush = QBrush(color)
                        pen = QPen(Qt.GlobalColor.black, 1)
                        building_rect = self.scene.addRect(rect, pen, brush)
                        building_rect.setZValue(1)
                
                # Show preview only for hover tile with selected building
                if (self.selected_building and 
                    x == self.hover_tile_x and y == self.hover_tile_y and
                    self.hover_tile_x >= 0 and self.hover_tile_y >= 0):
                    
                    self._draw_building_preview(pos_x, pos_y, rect)
                
                # Add tile border (Z-level 2)
                border_pen = QPen(Qt.GlobalColor.black, 1)
                border_rect = self.scene.addRect(rect, border_pen, QBrush(Qt.BrushStyle.NoBrush))
                border_rect.setZValue(2)
                
                # Add highlights (Z-level 3)
                self._draw_tile_highlights(x, y, rect)
        
        # Set scene rect once at the end
        self.scene.setSceneRect(0, 0, scene_width, scene_height)
    
    def _draw_building_preview(self, pos_x: float, pos_y: float, rect: QRectF):
        """Draw building preview at hover position"""
        building_path = self.selected_building.get_image_path()
        if building_path:
            preview_pixmap = self.get_tile_image(building_path)
            
            # Apply rotation preview using preview_rotation
            if self.preview_rotation != 0:
                transform = QTransform()
                transform.translate(self.tile_size/2, self.tile_size/2)
                transform.rotate(self.preview_rotation)
                transform.translate(-self.tile_size/2, -self.tile_size/2)
                preview_pixmap = preview_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            
            # Add semi-transparent preview
            preview_item = self.scene.addPixmap(preview_pixmap)
            preview_item.setPos(pos_x, pos_y)
            preview_item.setOpacity(0.7)  # Semi-transparent preview
            preview_item.setZValue(1.5)  # Between building and border
            
            # Add rotation indicator for rotatable buildings
            if self.preview_rotation != 0:
                self._draw_rotation_arrow(pos_x, pos_y)
        else:
            # Show colored preview for buildings without images
            color = QColor(self.selected_building.get_color())
            color.setAlpha(180)  # Semi-transparent
            brush = QBrush(color)
            pen = QPen(Qt.GlobalColor.black, 1)
            preview_rect = self.scene.addRect(rect, pen, brush)
            preview_rect.setZValue(1.5)
            
            # Add rotation indicator for colored buildings too
            if self.preview_rotation != 0:
                self._draw_rotation_text(pos_x, pos_y)
    
    def _draw_rotation_arrow(self, pos_x: float, pos_y: float):
        """Draw rotation arrow indicator"""
        arrow_size = 8
        arrow_pixmap = QPixmap(arrow_size * 2, arrow_size * 2)
        arrow_pixmap.fill(Qt.GlobalColor.transparent)
        
        arrow_painter = QPainter(arrow_pixmap)
        arrow_painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        arrow_painter.setBrush(QBrush(Qt.GlobalColor.yellow))
        
        # Draw arrow pointing right (will be rotated)
        arrow_points = [
            QPointF(arrow_size * 0.5, arrow_size),
            QPointF(arrow_size * 1.5, arrow_size),
            QPointF(arrow_size * 1.8, arrow_size * 1.3),
        ]
        arrow_painter.drawPolygon(arrow_points)
        arrow_painter.end()
        
        # Rotate arrow to match building rotation
        if self.preview_rotation != 0:
            arrow_transform = QTransform()
            arrow_transform.translate(arrow_size, arrow_size)
            arrow_transform.rotate(self.preview_rotation)
            arrow_transform.translate(-arrow_size, -arrow_size)
            arrow_pixmap = arrow_pixmap.transformed(arrow_transform, Qt.TransformationMode.SmoothTransformation)
        
        arrow_item = self.scene.addPixmap(arrow_pixmap)
        arrow_item.setPos(pos_x + self.tile_size - arrow_size * 2, pos_y)
        arrow_item.setZValue(2.5)  # On top of everything
    
    def _draw_rotation_text(self, pos_x: float, pos_y: float):
        """Draw rotation text indicator"""
        from PyQt6.QtWidgets import QGraphicsTextItem
        from PyQt6.QtGui import QFont
        
        rotation_text = QGraphicsTextItem(f"{self.preview_rotation}°")
        rotation_text.setDefaultTextColor(Qt.GlobalColor.white)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        rotation_text.setFont(font)
        rotation_text.setPos(pos_x + 2, pos_y + 2)
        rotation_text.setZValue(2.5)
        self.scene.addItem(rotation_text)
    
    def _draw_tile_highlights(self, x: int, y: int, rect: QRectF):
        """Draw tile highlights for selection and hover"""
        tile = self.city_map.get_tile(x, y)
        highlight_needed = False
        highlight_color = Qt.GlobalColor.yellow
        
        # Check if this is the hovered tile with building selected
        if (self.selected_building and 
            x == self.hover_tile_x and y == self.hover_tile_y and
            self.hover_tile_x >= 0 and self.hover_tile_y >= 0):
            highlight_needed = True
            if self.can_build(x, y):
                highlight_color = Qt.GlobalColor.green  # Green for buildable
            else:
                highlight_color = Qt.GlobalColor.red    # Red for non-buildable
        
        # Check if this is the selected tile
        elif tile == self.city_map.get_selected_tile():
            highlight_needed = True
            highlight_color = Qt.GlobalColor.yellow  # Yellow for selected
        
        if highlight_needed:
            highlight_pen = QPen(highlight_color, 3)
            highlight_rect = self.scene.addRect(rect, highlight_pen, QBrush(Qt.BrushStyle.NoBrush))
            highlight_rect.setZValue(3)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handles mouse click events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert click position to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            
            # Calculate tile coordinates
            tile_x = int(scene_pos.x() // self.tile_size)
            tile_y = int(scene_pos.y() // self.tile_size)
            
            # Check if coordinates are within map bounds
            if (0 <= tile_x < self.city_map.width and 0 <= tile_y < self.city_map.height):
                if self.selected_building:
                    # Try to place building
                    self.place_building(tile_x, tile_y)
                    # Deselect tile when placing building
                    self.city_map.deselect_tile()
                else:
                    # Toggle tile selection
                    current_selection = self.city_map.get_selected_tile()
                    tile = self.city_map.get_tile(tile_x, tile_y)
                    
                    if current_selection == tile:
                        # If clicking same tile, deselect it
                        self.city_map.deselect_tile()
                    else:
                        # Select new tile
                        self.city_map.select_tile(tile_x, tile_y)
                        self.tile_clicked.emit(tile_x, tile_y)
                
                # Redraw map
                self.draw_map()
        
        elif event.button() == Qt.MouseButton.RightButton:
            # Sprzedaż budynku po PPM
            scene_pos = self.mapToScene(event.pos())
            tile_x = int(scene_pos.x() // self.tile_size)
            tile_y = int(scene_pos.y() // self.tile_size)
            tile = self.city_map.get_tile(tile_x, tile_y)
            if tile and tile.building:
                self.building_sell_requested.emit(tile_x, tile_y, tile.building)
            else:
                # If no building selected, deselect tile on right click
                if self.city_map.get_selected_tile() is not None:
                    self.city_map.deselect_tile()
                    self.draw_map()
    
    def keyPressEvent(self, event):
        """Handles key press events"""
        if event.key() == Qt.Key.Key_R and self.selected_building:
            self.rotate_building()
        elif event.key() == Qt.Key.Key_Escape:
            # Escape key deselects building and tile
            if self.selected_building:
                self.selected_building = None
                self.preview_rotation = 0
                self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # Also deselect any selected tile
            if self.city_map.get_selected_tile():
                self.city_map.deselect_tile()
                
            # Pełne przerysowanie po zmianie stanu
            self.draw_map()
        else:
            super().keyPressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handles mouse move events for hover preview"""
        # Throttle updates to improve performance and prevent rapid object creation/deletion
        current_time = time.time()
        if current_time - self._last_update_time < 0.15:  # Zwiększone z 0.1 na 0.15 dla stabilności
            super().mouseMoveEvent(event)
            return
        
        # Convert mouse position to scene coordinates
        scene_pos = self.mapToScene(event.pos())
        
        # Calculate tile coordinates
        new_hover_x = int(scene_pos.x() // self.tile_size)
        new_hover_y = int(scene_pos.y() // self.tile_size)
        
        # Update hover position if changed and within bounds
        if (new_hover_x != self.hover_tile_x or new_hover_y != self.hover_tile_y):
            # Check if coordinates are within map bounds
            if (0 <= new_hover_x < self.city_map.width and 
                0 <= new_hover_y < self.city_map.height):
                
                self.hover_tile_x = new_hover_x
                self.hover_tile_y = new_hover_y
                
                # Only redraw if we have a selected building
                if self.selected_building:
                    # Rozwiązanie radykalne: pełne przerysowanie mapy za każdym razem
                    # Eliminuje wszystkie artefakty kosztem wydajności
                    self.draw_map()
                    self._last_update_time = current_time
        
        super().mouseMoveEvent(event)
    
    def _cleanup_artifacts(self):
        """Clean up any remaining preview artifacts"""
        # Get all items with Z-value indicating they might be preview items
        try:
            all_items = self.scene.items()
        except:
            return  # Scene might be invalid
        
        artifacts_removed = 0
        
        for item in all_items:
            try:
                # Check if item is valid before accessing properties
                if not hasattr(item, 'zValue'):
                    continue
                    
                z_value = item.zValue()
                # Remove items that look like preview artifacts (Z-value 1.5, 2.5, or 3)
                if z_value in [1.5, 2.5, 3.0] and item not in self._preview_items:
                    # Double check the item is still valid
                    if hasattr(item, 'scene') and item.scene() == self.scene:
                        self.scene.removeItem(item)
                        artifacts_removed += 1
            except (RuntimeError, AttributeError):
                # Item already deleted or invalid - skip it
                continue
        
        # Limit artifacts cleanup to prevent performance issues
        if artifacts_removed > 10:
            print(f"Cleaned up {artifacts_removed} preview artifacts")
    
    def _cleanup_all_previews(self):
        """Clean up all preview items safely"""
        try:
            # Make a copy of the list to avoid modification during iteration
            current_items = self._preview_items.copy()
            self._preview_items = []  # Clear the original list first
            
            for item in current_items:
                try:
                    if item and hasattr(item, 'scene') and item.scene() == self.scene:
                        self.scene.removeItem(item)
                except (RuntimeError, AttributeError):
                    pass  # Item might be already deleted
            
            # Also run artifact cleanup
            self._cleanup_artifacts()
            
            # Force a full redraw every few operations to reset the scene
            if random.random() < 0.2:  # 20% chance for full redraw
                self.draw_map()
                
        except Exception as e:
            print(f"Error in cleanup: {e}")  # Debug info
    
    def update_preview_only(self):
        """Updates only the building preview without redrawing entire map"""
        # Safety first - clean up all existing previews before adding new ones
        self._cleanup_all_previews_immediate()
        
        # Add new preview if we have selected building and valid hover position
        if (self.selected_building and 
            self.hover_tile_x >= 0 and self.hover_tile_y >= 0 and
            self.hover_tile_x < self.city_map.width and 
            self.hover_tile_y < self.city_map.height):
            
            pos_x = self.hover_tile_x * self.tile_size
            pos_y = self.hover_tile_y * self.tile_size
            rect = QRectF(pos_x, pos_y, self.tile_size, self.tile_size)
            
            # Draw building preview
            building_path = self.selected_building.get_image_path()
            if building_path:
                preview_pixmap = self.get_tile_image(building_path)
                
                # Apply rotation preview
                if self.preview_rotation != 0:
                    transform = QTransform()
                    transform.translate(self.tile_size/2, self.tile_size/2)
                    transform.rotate(self.preview_rotation)
                    transform.translate(-self.tile_size/2, -self.tile_size/2)
                    preview_pixmap = preview_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
                
                # Add semi-transparent preview
                preview_item = self.scene.addPixmap(preview_pixmap)
                preview_item.setPos(pos_x, pos_y)
                preview_item.setOpacity(0.7)
                preview_item.setZValue(1.5)
                self._preview_items.append(preview_item)
                
                # Add rotation indicator
                if self.preview_rotation != 0:
                    arrow_item = self._create_rotation_arrow(pos_x, pos_y)
                    if arrow_item:
                        self._preview_items.append(arrow_item)
            else:
                # Colored preview
                color = QColor(self.selected_building.get_color())
                color.setAlpha(180)
                brush = QBrush(color)
                pen = QPen(Qt.GlobalColor.black, 1)
                preview_rect = self.scene.addRect(rect, pen, brush)
                preview_rect.setZValue(1.5)
                self._preview_items.append(preview_rect)
                
                # Add rotation text
                if self.preview_rotation != 0:
                    text_item = self._create_rotation_text(pos_x, pos_y)
                    if text_item:
                        self._preview_items.append(text_item)
            
            # Add highlight
            highlight_color = Qt.GlobalColor.green if self.can_build(self.hover_tile_x, self.hover_tile_y) else Qt.GlobalColor.red
            highlight_pen = QPen(highlight_color, 3)
            highlight_rect = self.scene.addRect(rect, highlight_pen, QBrush(Qt.BrushStyle.NoBrush))
            highlight_rect.setZValue(3)
            self._preview_items.append(highlight_rect)
    
    def _cleanup_all_previews_immediate(self):
        """Clean up all preview items immediately (non-delayed version)"""
        try:
            # Make sure we're not operating on a deleted scene
            if not self.scene:
                self._preview_items = []
                return
                
            # Make a copy to avoid modification during iteration
            current_items = self._preview_items.copy()
            self._preview_items = []  # Clear list first
            
            for item in current_items:
                try:
                    if item and hasattr(item, 'scene') and item.scene() == self.scene:
                        self.scene.removeItem(item)
                except (RuntimeError, AttributeError):
                    pass  # Item might be already deleted
                    
        except Exception as e:
            print(f"Error in immediate cleanup: {e}")
    
    def _create_rotation_arrow(self, pos_x: float, pos_y: float):
        """Create rotation arrow and return the graphics item"""
        arrow_size = 8
        arrow_pixmap = QPixmap(arrow_size * 2, arrow_size * 2)
        arrow_pixmap.fill(Qt.GlobalColor.transparent)
        
        arrow_painter = QPainter(arrow_pixmap)
        arrow_painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        arrow_painter.setBrush(QBrush(Qt.GlobalColor.yellow))
        
        arrow_points = [
            QPointF(arrow_size * 0.5, arrow_size),
            QPointF(arrow_size * 1.5, arrow_size),
            QPointF(arrow_size * 1.8, arrow_size * 1.3),
        ]
        arrow_painter.drawPolygon(arrow_points)
        arrow_painter.end()
        
        # Rotate arrow
        if self.preview_rotation != 0:
            arrow_transform = QTransform()
            arrow_transform.translate(arrow_size, arrow_size)
            arrow_transform.rotate(self.preview_rotation)
            arrow_transform.translate(-arrow_size, -arrow_size)
            arrow_pixmap = arrow_pixmap.transformed(arrow_transform, Qt.TransformationMode.SmoothTransformation)
        
        arrow_item = self.scene.addPixmap(arrow_pixmap)
        arrow_item.setPos(pos_x + self.tile_size - arrow_size * 2, pos_y)
        arrow_item.setZValue(2.5)
        return arrow_item
    
    def _create_rotation_text(self, pos_x: float, pos_y: float):
        """Create rotation text and return the graphics item"""
        from PyQt6.QtWidgets import QGraphicsTextItem
        from PyQt6.QtGui import QFont
        
        rotation_text = QGraphicsTextItem(f"{self.preview_rotation}°")
        rotation_text.setDefaultTextColor(Qt.GlobalColor.white)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        rotation_text.setFont(font)
        rotation_text.setPos(pos_x + 2, pos_y + 2)
        rotation_text.setZValue(2.5)
        self.scene.addItem(rotation_text)
        return rotation_text

    def wheelEvent(self, event: QWheelEvent):
        """Handles mouse wheel events for zooming"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom factor
            zoom_in = event.angleDelta().y() > 0
            factor = 1.1 if zoom_in else 0.9
            
            # Apply zoom
            self.scale(factor, factor)
            self.zoom_factor *= factor
        else:
            # Normal scrolling
            super().wheelEvent(event) 