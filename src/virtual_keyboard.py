import cv2
import numpy as np


class VirtualKeyboard:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.visible = False
        
        # Keyboard layout
        self.keys = [
            ['G', 'B', 'R', 'Y', 'W', 'P', 'O', 'C'],  # Colors
            ['1', '2', '3', '4', '5'],  # Thickness
            ['NORMAL', 'CIRCLE', 'SQUARE', 'SPRAY'],  # Brush shapes
            ['SAVE', 'CLEAR', 'UNDO', 'HIDE']  # Actions
        ]
        
        self.key_labels = {
            'G': 'Green', 'B': 'Blue', 'R': 'Red', 'Y': 'Yellow',
            'W': 'White', 'P': 'Purple', 'O': 'Orange', 'C': 'Cyan',
            '1': 'Size:3', '2': 'Size:5', '3': 'Size:8', '4': 'Size:12', '5': 'Size:20',
            'SAVE': 'Save', 'CLEAR': 'Clear', 'UNDO': 'Undo', 'HIDE': 'Hide KB'
        }
        
        # Key dimensions
        self.key_width = 100
        self.key_height = 60
        self.key_margin = 10
        
        # Keyboard position (bottom center)
        self.keyboard_height = (len(self.keys) * (self.key_height + self.key_margin)) + 20
        self.start_y = height - self.keyboard_height - 10
        
        # Hover state
        self.hovered_key = None
        self.last_clicked_key = None
        self.click_cooldown = 0
    
    def toggle_visibility(self):
        """Toggle keyboard visibility"""
        self.visible = not self.visible
        return self.visible
    
    def draw(self, frame):
        """Draw virtual keyboard on frame"""
        if not self.visible:
            return frame
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (0, self.start_y - 10), 
                     (self.width, self.height),
                     (40, 40, 40), 
                     -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        # Draw keys
        y_pos = self.start_y
        for row in self.keys:
            # Calculate starting x position to center the row
            row_width = len(row) * (self.key_width + self.key_margin)
            x_pos = (self.width - row_width) // 2
            
            for key in row:
                # Check if hovered
                is_hovered = (self.hovered_key == key)
                
                # Key background
                key_color = (80, 80, 80) if not is_hovered else (120, 120, 120)
                cv2.rectangle(frame,
                            (x_pos, y_pos),
                            (x_pos + self.key_width, y_pos + self.key_height),
                            key_color,
                            -1)
                
                # Key border
                cv2.rectangle(frame,
                            (x_pos, y_pos),
                            (x_pos + self.key_width, y_pos + self.key_height),
                            (200, 200, 200),
                            2)
                
                # Key label
                label = self.key_labels.get(key, key)
                font_scale = 0.5 if len(label) > 6 else 0.7
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
                text_x = x_pos + (self.key_width - text_size[0]) // 2
                text_y = y_pos + (self.key_height + text_size[1]) // 2
                
                cv2.putText(frame, label,
                          (text_x, text_y),
                          cv2.FONT_HERSHEY_SIMPLEX,
                          font_scale,
                          (255, 255, 255),
                          2)
                
                x_pos += self.key_width + self.key_margin
            
            y_pos += self.key_height + self.key_margin
        
        # Instructions
        cv2.putText(frame, "Point at a key with index finger to select",
                   (self.width // 2 - 250, self.start_y - 20),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.6,
                   (255, 255, 255),
                   1)
        
        return frame
    
    def check_hover(self, point):
        """Check if point is hovering over any key"""
        if not self.visible:
            return None
        
        x, y = point
        
        y_pos = self.start_y
        for row in self.keys:
            row_width = len(row) * (self.key_width + self.key_margin)
            x_pos = (self.width - row_width) // 2
            
            for key in row:
                if (x_pos <= x <= x_pos + self.key_width and
                    y_pos <= y <= y_pos + self.key_height):
                    self.hovered_key = key
                    return key
                
                x_pos += self.key_width + self.key_margin
            
            y_pos += self.key_height + self.key_margin
        
        self.hovered_key = None
        return None
    
    def click_key(self, key):
        """Handle key click with cooldown"""
        if self.click_cooldown > 0:
            return None
        
        if key and key != self.last_clicked_key:
            self.last_clicked_key = key
            self.click_cooldown = 15  # Frames cooldown
            return key
        
        return None
    
    def update_cooldown(self):
        """Update click cooldown"""
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
            if self.click_cooldown == 0:
                self.last_clicked_key = None