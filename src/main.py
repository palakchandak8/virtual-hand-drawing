import cv2
import numpy as np
from gesture_detector import GestureDetector
from drawing_canvas import DrawingCanvas
from virtual_keyboard import VirtualKeyboard
from notification_system import NotificationSystem


class VirtualDrawingApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to access webcam")
        
        h, w, _ = frame.shape
        
        # SLOWED DOWN: Increased smoothing from 5 to 10 frames
        self.detector = GestureDetector(smoothing_frames=10)
        self.canvas = DrawingCanvas(w, h)
        self.keyboard = VirtualKeyboard(w, h)
        self.notifications = NotificationSystem()
        
        self.current_gesture = "NONE"
        self.prev_gesture = "NONE"
        
        # UI settings
        self.show_instructions = True
        self.show_ribbon = True
        self.paused = False
        
        # Pinch gesture state
        self.pinch_base_distance = None
        self.pinch_base_thickness = None
        
        # Text placement mode
        self.text_placement_mode = False
        self.text_position = None
        
    def draw_ui_ribbon(self, frame):
        """Draw UI ribbon with controls"""
        if not self.show_ribbon:
            return frame
        
        h, w, _ = frame.shape
        
        # Ribbon background
        overlay = frame.copy()
        ribbon_height = 120
        cv2.rectangle(overlay, (0, 0), (w, ribbon_height), (50, 50, 50), -1)
        
        # Status section with PAUSE indicator
        status_text = f"Gesture: {self.current_gesture}"
        if self.paused:
            status_text += " [PAUSED]"
            cv2.putText(overlay, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            cv2.putText(overlay, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Color palette preview
        palette_x = 10
        palette_y = 50
        cv2.putText(overlay, "Colors:", (palette_x, palette_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        palette_x += 80
        for key, color in self.canvas.colors.items():
            # Draw color box
            is_selected = (color == self.canvas.current_color)
            thickness = 3 if is_selected else 1
            
            cv2.rectangle(overlay, 
                         (palette_x, palette_y - 15), 
                         (palette_x + 30, palette_y + 5),
                         color, -1)
            cv2.rectangle(overlay, 
                         (palette_x, palette_y - 15), 
                         (palette_x + 30, palette_y + 5),
                         (255, 255, 255), thickness)
            
            # Draw key label
            cv2.putText(overlay, key.upper(), 
                       (palette_x + 8, palette_y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            palette_x += 40
        
        # Brush shapes
        brush_x = palette_x + 30
        cv2.putText(overlay, f"Brush: {self.canvas.current_brush_shape}", 
                   (brush_x, palette_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Thickness indicator
        thickness_x = brush_x + 200
        cv2.putText(overlay, f"Thickness: {self.canvas.brush_thickness}", 
                   (thickness_x, palette_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw thickness preview circle
        cv2.circle(overlay, 
                  (thickness_x + 150, palette_y - 5),
                  self.canvas.brush_thickness,
                  self.canvas.current_color, -1)
        cv2.circle(overlay, 
                  (thickness_x + 150, palette_y - 5),
                  self.canvas.brush_thickness,
                  (255, 255, 255), 1)
        
        # Instructions line 2
        controls_y = palette_y + 40
        cv2.putText(overlay, "NEW: [Index] Draw | [Fist] Erase All | [Palm] Pause | [2 Fingers] Undo | [3 Fingers] Brush | [Pinch] Size", 
                   (10, controls_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        # Keyboard instructions (T for Toggle Ribbon)
        cv2.putText(overlay, "Keys: K (Keyboard) | G/B/R/Y/W/P/O/C (Colors) | S (Save) | Q (Quit) | H (Help) | T (Toggle Ribbon)",
                   (10, controls_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        # Blend overlay
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        return frame
    
    def draw_side_instructions(self, frame):
        """Draw side panel instructions"""
        if not self.show_instructions or not self.show_ribbon:
            return frame
        
        h, w, _ = frame.shape
        
        instructions = [
            "GESTURES (UPDATED):",
            "Index: Draw",
            "Fist: Erase ALL",
            "Palm: Pause/Verify",
            "Two fingers: Undo",
            "Three fingers: Brush",
            "Pinch: Thickness",
            "",
            "KEYBOARD:",
            "K: QWERTY Keyboard",
            "G/B/R/Y/W/P/O/C: Colors",
            "S: Save (output folder)",
            "Q: Quit app",
            "H: Toggle help",
            "T: Toggle ribbon",
        ]
        
        # Draw semi-transparent background
        overlay = frame.copy()
        panel_width = 250
        cv2.rectangle(overlay, (w - panel_width, 130), (w, 130 + len(instructions) * 25 + 20), 
                     (40, 40, 40), -1)
        
        y_offset = 150
        for instruction in instructions:
            if instruction == "":
                y_offset += 10
                continue
            
            font_scale = 0.5 if instruction.endswith(":") else 0.45
            font_thickness = 2 if instruction.endswith(":") else 1
            
            cv2.putText(overlay, instruction, (w - panel_width + 10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
            y_offset += 25
        
        # Blend overlay
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        return frame
    
    def handle_pinch_gesture(self, landmarks, frame_shape):
        """Handle pinch gesture for thickness control"""
        distance, thumb_pos, index_pos = self.detector.get_pinch_distance(landmarks, frame_shape)
        
        if self.pinch_base_distance is None:
            self.pinch_base_distance = distance
            self.pinch_base_thickness = self.canvas.brush_thickness
        
        # Calculate new thickness based on pinch distance change
        distance_ratio = distance / self.pinch_base_distance
        new_thickness = int(self.pinch_base_thickness * distance_ratio)
        self.canvas.set_thickness(new_thickness)
        
        # Visual feedback
        return thumb_pos, index_pos
    
    def run(self):
        """Main application loop"""
        print("=" * 60)
        print("  VIRTUAL HAND-DRAWING APP - ENHANCED VERSION")
        print("=" * 60)
        print("\nNEW GESTURE CONTROLS:")
        print("  - Index finger: Draw")
        print("  - Closed fist: ERASE ALL")
        print("  - Open palm: PAUSE/VERIFY")
        print("  - Two fingers: Undo")
        print("  - Three fingers: Change brush")
        print("  - Pinch: Adjust thickness")
        print("\nKEYBOARD:")
        print("  - K: QWERTY Virtual Keyboard")
        print("  - G/B/R/Y/W/P/O/C: Colors")
        print("  - S: Save to output folder")
        print("  - Q: Quit")
        print("  - T: Toggle ribbon")
        print("=" * 60)
        
        self.notifications.add_notification("App Started! Press K for keyboard", 3.0, 'info')
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)  # Mirror the frame
            
            # Detect hands
            results = self.detector.detect_hands(frame)
            
            if results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0].landmark
                
                # Get finger states and detect gesture
                fingers_up = self.detector.get_finger_states(landmarks)
                self.current_gesture = self.detector.detect_gesture(fingers_up, landmarks, frame.shape)
                
                # Get index finger position (smoothed)
                finger_pos = self.detector.get_index_finger_tip(
                    landmarks, frame.shape
                )
                
                # Check keyboard interaction
                if self.keyboard.visible:
                    hovered_key = self.keyboard.check_hover(finger_pos)
                    
                    # Click on keyboard key when drawing gesture over key
                    if self.current_gesture == "DRAW" and hovered_key:
                        clicked_key = self.keyboard.click_key(hovered_key)
                        if clicked_key == 'SAVE':
                            # Enter text placement mode
                            if self.keyboard.get_text():
                                self.text_placement_mode = True
                                self.notifications.add_notification("Point where to place text and draw", 3.0, 'info')
                        elif clicked_key == 'HIDE':
                            self.keyboard.toggle_visibility()
                            self.notifications.add_notification("Keyboard hidden", 1.5, 'info')
                
                # Text placement mode
                elif self.text_placement_mode:
                    if self.current_gesture == "DRAW":
                        # Place text at finger position
                        text = self.keyboard.get_text()
                        if text:
                            self.canvas.add_text(text, finger_pos)
                            self.notifications.add_notification(f"Text placed: {text}", 2.0, 'success')
                        self.text_placement_mode = False
                        self.keyboard.clear_text()
                
                # Handle gestures (only if not interacting with keyboard)
                elif not self.paused:
                    if self.current_gesture == "DRAW":
                        if self.prev_gesture != "DRAW":
                            self.canvas.start_stroke()
                        self.canvas.draw(finger_pos)
                        # Draw visual indicator
                        cv2.circle(frame, finger_pos, 8, self.canvas.current_color, -1)
                        cv2.circle(frame, finger_pos, 10, (255, 255, 255), 2)
                    
                    elif self.current_gesture == "ERASE_ALL":
                        if self.prev_gesture != "ERASE_ALL":
                            self.canvas.erase_all()
                            self.notifications.add_notification("Canvas erased!", 2.0, 'warning')
                    
                    elif self.current_gesture == "PAUSE":
                        if self.prev_gesture != "PAUSE":
                            self.paused = not self.paused
                            if self.paused:
                                self.notifications.add_notification("PAUSED - Show palm again to resume", 2.0, 'info')
                            else:
                                self.notifications.add_notification("Resumed drawing", 1.5, 'success')
                    
                    elif self.current_gesture == "UNDO":
                        if self.prev_gesture != "UNDO":
                            self.canvas.undo()
                            self.notifications.add_notification("Undo last stroke", 1.5, 'info')
                    
                    elif self.current_gesture == "THREE_FINGERS":
                        if self.prev_gesture != "THREE_FINGERS":
                            new_shape = self.canvas.next_brush_shape()
                            self.notifications.add_notification(f"Brush: {new_shape}", 1.5, 'info')
                    
                    elif self.current_gesture == "PINCH":
                        thumb_pos, index_pos = self.handle_pinch_gesture(landmarks, frame.shape)
                        # Draw line between thumb and index
                        cv2.line(frame, thumb_pos, index_pos, (255, 0, 255), 2)
                        cv2.circle(frame, thumb_pos, 8, (255, 0, 255), -1)
                        cv2.circle(frame, index_pos, 8, (255, 0, 255), -1)
                    
                    else:
                        if self.prev_gesture == "DRAW":
                            self.canvas.end_stroke()
                        if self.prev_gesture == "PINCH":
                            self.pinch_base_distance = None
                            self.pinch_base_thickness = None
                
                # Pause mode - show indicator
                if self.paused:
                    if self.current_gesture == "PAUSE":
                        if self.prev_gesture != "PAUSE":
                            self.paused = False
                            self.notifications.add_notification("Resumed!", 1.5, 'success')
                    
                    # Draw pause indicator
                    cv2.circle(frame, finger_pos, 30, (0, 165, 255), 5)
                    cv2.putText(frame, "PAUSED", 
                               (finger_pos[0] - 50, finger_pos[1] - 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                
                # Draw hand landmarks
                frame = self.detector.draw_hand_landmarks(frame, results)
                
                self.prev_gesture = self.current_gesture
            else:
                self.current_gesture = "NONE"
                if self.prev_gesture == "DRAW":
                    self.canvas.end_stroke()
                if self.prev_gesture == "PINCH":
                    self.pinch_base_distance = None
                    self.pinch_base_thickness = None
                self.prev_gesture = "NONE"
            
            # Update keyboard cooldown
            self.keyboard.update_cooldown()
            
            # Composite: webcam + drawing canvas
            canvas_overlay = self.canvas.get_canvas()
            frame = cv2.addWeighted(frame, 0.7, canvas_overlay, 0.3, 0)
            
            # Draw UI elements
            frame = self.draw_ui_ribbon(frame)
            frame = self.draw_side_instructions(frame)
            frame = self.keyboard.draw(frame)
            frame = self.notifications.draw(frame)
            
            # Display
            cv2.imshow("Virtual Hand-Drawing", frame)
            
            # SLOWED DOWN: Changed from 1ms to 30ms delay
            key = cv2.waitKey(10) & 0xFF
            
            if key == ord('q'):
                self.notifications.add_notification("Exiting application...", 1.0, 'info')
                print("\nExiting application...")
                break
            elif key == ord('s'):
                filename = self.canvas.save_canvas()
                self.notifications.add_notification(f"Saved: {filename}", 3.0, 'success')
                print(f"Drawing saved: {filename}")
            elif key == ord('h'):
                self.show_instructions = not self.show_instructions
                status = "shown" if self.show_instructions else "hidden"
                self.notifications.add_notification(f"Help {status}", 1.0, 'info')
            elif key == ord('t'):  # Changed from 'r' to 't'
                self.show_ribbon = not self.show_ribbon
                status = "shown" if self.show_ribbon else "hidden"
                self.notifications.add_notification(f"Ribbon {status}", 1.0, 'info')
            elif key == ord('k'):
                was_visible = self.keyboard.visible
                self.keyboard.toggle_visibility()
                if self.keyboard.visible:
                    self.notifications.add_notification("QWERTY Keyboard opened", 2.0, 'info')
                else:
                    self.notifications.add_notification("Keyboard closed", 1.0, 'info')
            else:
                # Color change keys
                if chr(key) in self.canvas.colors:
                    self.canvas.change_color(chr(key))
                    color_name = self.canvas.get_color_name()
                    self.notifications.add_notification(f"Color: {color_name}", 1.5, 'info')
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("Application closed. Goodbye!")


if __name__ == "__main__":
    try:
        app = VirtualDrawingApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()