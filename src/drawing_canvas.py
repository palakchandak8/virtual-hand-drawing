import cv2
import numpy as np
from datetime import datetime
import random


class DrawingCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Drawing settings
        self.current_color = (0, 255, 0)  # Green
        self.brush_thickness = 5
        self.eraser_thickness = 30
        
        # Brush shapes
        self.brush_shapes = ['NORMAL', 'CIRCLE', 'SQUARE', 'SPRAY']
        self.current_brush_shape = 'NORMAL'
        self.brush_shape_index = 0
        
        # Drawing state
        self.is_drawing = False
        self.last_point = None
        
        # Stroke history for undo
        self.stroke_history = []
        self.current_stroke = []
        
        # Text input
        self.text_input = ""
        self.text_position = None
        
        # Color palette
        self.colors = {
            'g': (0, 255, 0),      # Green
            'b': (255, 0, 0),      # Blue
            'r': (0, 0, 255),      # Red
            'y': (0, 255, 255),    # Yellow
            'w': (255, 255, 255),  # White
            'p': (255, 0, 255),    # Purple
            'o': (0, 165, 255),    # Orange
            'c': (255, 255, 0),    # Cyan
        }
        
        self.color_names = {
            (0, 255, 0): 'Green',
            (255, 0, 0): 'Blue',
            (0, 0, 255): 'Red',
            (0, 255, 255): 'Yellow',
            (255, 255, 255): 'White',
            (255, 0, 255): 'Purple',
            (0, 165, 255): 'Orange',
            (255, 255, 0): 'Cyan',
        }
    
    def draw(self, point):
        """Draw on canvas with current brush shape"""
        if self.current_brush_shape == 'NORMAL':
            self._draw_normal(point)
        elif self.current_brush_shape == 'CIRCLE':
            self._draw_circle(point)
        elif self.current_brush_shape == 'SQUARE':
            self._draw_square(point)
        elif self.current_brush_shape == 'SPRAY':
            self._draw_spray(point)
    
    def _draw_normal(self, point):
        """Normal line drawing"""
        if self.last_point is not None:
            cv2.line(
                self.canvas,
                self.last_point,
                point,
                self.current_color,
                self.brush_thickness
            )
            self.current_stroke.append({
                'start': self.last_point,
                'end': point,
                'color': self.current_color,
                'thickness': self.brush_thickness,
                'shape': 'NORMAL'
            })
        self.last_point = point
    
    def _draw_circle(self, point):
        """Draw with circular brush - INCREASED OPACITY"""
        # Draw multiple overlapping circles for better visibility
        for radius_offset in range(0, self.brush_thickness + 1, max(1, self.brush_thickness // 3)):
            cv2.circle(
                self.canvas,
                point,
                self.brush_thickness - radius_offset,
                self.current_color,
                -1
            )
        
        if self.last_point:
            self.current_stroke.append({
                'point': point,
                'color': self.current_color,
                'thickness': self.brush_thickness,
                'shape': 'CIRCLE'
            })
        self.last_point = point
    
    def _draw_square(self, point):
        """Draw with square brush - INCREASED OPACITY"""
        half_size = self.brush_thickness
        top_left = (point[0] - half_size, point[1] - half_size)
        bottom_right = (point[0] + half_size, point[1] + half_size)
        
        # Draw filled square
        cv2.rectangle(
            self.canvas,
            top_left,
            bottom_right,
            self.current_color,
            -1
        )
        
        # Draw additional smaller square for better fill
        cv2.rectangle(
            self.canvas,
            (point[0] - half_size//2, point[1] - half_size//2),
            (point[0] + half_size//2, point[1] + half_size//2),
            self.current_color,
            -1
        )
        
        if self.last_point:
            self.current_stroke.append({
                'point': point,
                'color': self.current_color,
                'thickness': self.brush_thickness,
                'shape': 'SQUARE'
            })
        self.last_point = point
    
    def _draw_spray(self, point):
        """Draw with spray paint effect - INCREASED DENSITY"""
        num_particles = 40  # Increased from 20
        for _ in range(num_particles):
            offset_x = random.randint(-self.brush_thickness*2, self.brush_thickness*2)
            offset_y = random.randint(-self.brush_thickness*2, self.brush_thickness*2)
            
            spray_point = (point[0] + offset_x, point[1] + offset_y)
            
            # Check bounds
            if 0 <= spray_point[0] < self.width and 0 <= spray_point[1] < self.height:
                # Draw larger particles with varying sizes
                particle_size = random.randint(1, 3)
                cv2.circle(
                    self.canvas,
                    spray_point,
                    particle_size,
                    self.current_color,
                    -1
                )
        
        if self.last_point:
            self.current_stroke.append({
                'point': point,
                'color': self.current_color,
                'thickness': self.brush_thickness,
                'shape': 'SPRAY'
            })
        self.last_point = point
    
    def erase_all(self):
        """Erase entire canvas (fist gesture)"""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.stroke_history = []
        self.current_stroke = []
        self.last_point = None
        self.text_input = ""
    
    def clear(self):
        """Clear entire canvas (same as erase_all, kept for compatibility)"""
        self.erase_all()
    
    def undo(self):
        """Undo last stroke"""
        if len(self.stroke_history) > 0:
            self.stroke_history.pop()
            self.redraw_from_history()
    
    def redraw_from_history(self):
        """Redraw canvas from stroke history"""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for stroke in self.stroke_history:
            for item in stroke:
                if item['shape'] == 'NORMAL':
                    cv2.line(
                        self.canvas,
                        item['start'],
                        item['end'],
                        item['color'],
                        item['thickness']
                    )
                elif item['shape'] == 'CIRCLE':
                    for radius_offset in range(0, item['thickness'] + 1, max(1, item['thickness'] // 3)):
                        cv2.circle(
                            self.canvas,
                            item['point'],
                            item['thickness'] - radius_offset,
                            item['color'],
                            -1
                        )
                elif item['shape'] == 'SQUARE':
                    half_size = item['thickness']
                    top_left = (item['point'][0] - half_size, item['point'][1] - half_size)
                    bottom_right = (item['point'][0] + half_size, item['point'][1] + half_size)
                    cv2.rectangle(self.canvas, top_left, bottom_right, item['color'], -1)
    
    def start_stroke(self):
        """Start a new stroke"""
        self.current_stroke = []
        self.last_point = None
    
    def end_stroke(self):
        """End current stroke and save to history"""
        if len(self.current_stroke) > 0:
            self.stroke_history.append(self.current_stroke.copy())
        self.current_stroke = []
        self.last_point = None
    
    def change_color(self, key):
        """Change brush color based on key press"""
        if key in self.colors:
            self.current_color = self.colors[key]
            return True
        return False
    
    def next_brush_shape(self):
        """Cycle to next brush shape"""
        self.brush_shape_index = (self.brush_shape_index + 1) % len(self.brush_shapes)
        self.current_brush_shape = self.brush_shapes[self.brush_shape_index]
        return self.current_brush_shape
    
    def set_thickness(self, thickness):
        """Set brush thickness"""
        self.brush_thickness = max(1, min(50, thickness))
    
    def get_color_name(self):
        """Get current color name"""
        return self.color_names.get(self.current_color, 'Custom')
    
    def add_text(self, text, position):
        """Add text to canvas"""
        if text and position:
            cv2.putText(
                self.canvas,
                text,
                position,
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                self.current_color,
                2
            )
            self.text_input = ""
    
    def save_canvas(self, output_dir="output"):
        """Save canvas to file"""
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/drawing_{timestamp}.png"
        cv2.imwrite(filename, self.canvas)
        return filename
    
    def get_canvas(self):
        """Get current canvas"""
        return self.canvas