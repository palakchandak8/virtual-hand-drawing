import cv2
import numpy as np


class VirtualKeyboard:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.visible = False
        
        # QWERTY Keyboard layout
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL'],
            ['SPACE', 'CLEAR', 'SAVE', 'HIDE']
        ]
        
        # Key dimensions
        self.key_width = 70
        self.key_height = 60
        self.key_margin = 8
        
        # Keyboard position (bottom center)
        self.keyboard_height = (len(self.keys) * (self.key_height + self.key_margin)) + 40
        self.start_y = height - self.keyboard_height - 10
        
        # Text input
        self.text_input = ""
        
        # Hover state
        self.hovered_key = None
        self.last_clicked_key = None
        self.click_cooldown = 0
    
    def toggle_visibility(self):
        """Toggle keyboard visibility"""
        self.visible = not self.visible
        return self.visible
    
    def draw(self, frame):
        """Draw QWERTY virtual keyboard on frame"""
        if not self.visible:
            return frame
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (0, self.start_y - 60), 
                     (self.width, self.height),
                     (30, 30, 30), 
                     -1)
        frame = cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)
        
        # Draw text input display
        text_display_y = self.start_y - 45
        cv2.rectangle(frame,
                     (20, text_display_y),
                     (self.width - 20, text_display_y + 30),
                     (50, 50, 50),
                     -1)
        cv2.rectangle(frame,
                     (20, text_display_y),
                     (self.width - 20, text_display_y + 30),
                     (200, 200, 200),
                     2)
        
        # Display current text
        display_text = self.text_input if self.text_input else "Type here..."
        cv2.putText(frame, display_text,
                   (30, text_display_y + 22),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.6,
                   (255, 255, 255) if self.text_input else (150, 150, 150),
                   2)
        
        # Draw keys
        y_pos = self.start_y
        for row_idx, row in enumerate(self.keys):
            # Calculate starting x position to center the row
            if row_idx == 0:  # First row (QWERTY)
                row_width = len(row) * (self.key_width + self.key_margin)
                x_pos = (self.width - row_width) // 2
            elif row_idx == 1:  # Second row (ASDFGH)
                row_width = len(row) * (self.key_width + self.key_margin)
                x_pos = (self.width - row_width) // 2 + 30
            elif row_idx == 2:  # Third row (ZXCVBN)
                row_width = len(row) * (self.key_width + self.key_margin)
                x_pos = (self.width - row_width) // 2 + 60
            else:  # Last row (special keys)
                row_width = len(row) * (self.key_width + self.key_margin) + 100
                x_pos = (self.width - row_width) // 2
            
            for key in row:
                # Check if hovered
                is_hovered = (self.hovered_key == key)
                
                # Adjust width for special keys
                key_w = self.key_width
                if key == 'SPACE':
                    key_w = self.key_width * 3
                elif key in ['CLEAR', 'SAVE', 'HIDE', 'DEL']:
                    key_w = self.key_width + 20
                
                # Key background
                key_color = (70, 70, 70) if not is_hovered else (100, 150, 100)
                cv2.rectangle(frame,
                            (x_pos, y_pos),
                            (x_pos + key_w, y_pos + self.key_height),
                            key_color,
                            -1)
                
                # Key border
                cv2.rectangle(frame,
                            (x_pos, y_pos),
                            (x_pos + key_w, y_pos + self.key_height),
                            (200, 200, 200),
                            2)
                
                # Key label
                font_scale = 0.5 if len(key) > 3 else 0.7
                text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
                text_x = x_pos + (key_w - text_size[0]) // 2
                text_y = y_pos + (self.key_height + text_size[1]) // 2
                
                cv2.putText(frame, key,
                          (text_x, text_y),
                          cv2.FONT_HERSHEY_SIMPLEX,
                          font_scale,
                          (255, 255, 255),
                          2)
                
                x_pos += key_w + self.key_margin
            
            y_pos += self.key_height + self.key_margin
        
        # Instructions
        cv2.putText(frame, "Point index finger to type | SAVE to place text on canvas",
                   (self.width // 2 - 300, self.start_y - 55),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.5,
                   (200, 200, 200),
                   1)
        
        return frame
    
    def check_hover(self, point):
        """Check if point is hovering over any key"""
        if not self.visible:
            return None
        
        x, y = point
        
        y_pos = self.start_y
        for row_idx, row in enumerate(self.keys):
            if row_idx == 0:
                row_width = len(row) * (self.key_width + self.key_margin)
                x_pos = (self.width - row_width) // 2
            elif row_idx == 1:
                row_width = len(row) * (self.key_width + self.key_margin)
                x_pos = (self.width - row_width) // 2 + 30
            elif row_idx == 2:
                row_width = len(row) * (self.key_width + self.key_margin)
                x_pos = (self.width - row_width) // 2 + 60
            else:
                row_width = len(row) * (self.key_width + self.key_margin) + 100
                x_pos = (self.width - row_width) // 2
            
            for key in row:
                key_w = self.key_width
                if key == 'SPACE':
                    key_w = self.key_width * 3
                elif key in ['CLEAR', 'SAVE', 'HIDE', 'DEL']:
                    key_w = self.key_width + 20
                
                if (x_pos <= x <= x_pos + key_w and
                    y_pos <= y <= y_pos + self.key_height):
                    self.hovered_key = key
                    return key
                
                x_pos += key_w + self.key_margin
            
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
            
            # Handle key press
            if key == 'SPACE':
                self.text_input += ' '
            elif key == 'DEL':
                self.text_input = self.text_input[:-1]
            elif key == 'CLEAR':
                self.text_input = ''
            elif key in ['SAVE', 'HIDE']:
                return key  # Return special commands
            elif len(key) == 1:  # Regular character
                self.text_input += key.lower()
            
            return key
        
        return None
    
    def update_cooldown(self):
        """Update click cooldown"""
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
            if self.click_cooldown == 0:
                self.last_clicked_key = None
    
    def get_text(self):
        """Get current text input"""
        return self.text_input
    
    def clear_text(self):
        """Clear text input"""
        self.text_input = ""