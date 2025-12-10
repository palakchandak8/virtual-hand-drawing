import cv2
import numpy as np
from datetime import datetime


class DrawingCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Drawing settings
        self.current_color = (0, 255, 0)  # Green
        self.brush_thickness = 5
        self.eraser_thickness = 30
        
        # Drawing state
        self.is_drawing = False
        self.last_point = None
        
        # Stroke history for undo
        self.stroke_history = []
        self.current_stroke = []
        
        # Color palette
        self.colors = {
            'g': (0, 255, 0),      # Green
            'b': (255, 0, 0),      # Blue
            'r': (0, 0, 255),      # Red
            'y': (0, 255, 255),    # Yellow
            'w': (255, 255, 255),  # White
            'p': (255, 0, 255),    # Purple
        }
    
    def draw(self, point):
        """Draw on canvas"""
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
                'thickness': self.brush_thickness
            })
        self.last_point = point
    
    def erase(self, point):
        """Erase at point"""
        cv2.circle(
            self.canvas,
            point,
            self.eraser_thickness,
            (0, 0, 0),
            -1
        )
        self.last_point = point
    
    def clear(self):
        """Clear entire canvas"""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.stroke_history = []
        self.current_stroke = []
        self.last_point = None
    
    def undo(self):
        """Undo last stroke"""
        if len(self.stroke_history) > 0:
            self.stroke_history.pop()
            self.redraw_from_history()
    
    def redraw_from_history(self):
        """Redraw canvas from stroke history"""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for stroke in self.stroke_history:
            for line in stroke:
                cv2.line(
                    self.canvas,
                    line['start'],
                    line['end'],
                    line['color'],
                    line['thickness']
                )
    
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
    
    def save_canvas(self, output_dir="output"):
        """Save canvas to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/drawing_{timestamp}.png"
        cv2.imwrite(filename, self.canvas)
        return filename
    
    def get_canvas(self):
        """Get current canvas"""
        return self.canvas