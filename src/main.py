import cv2
import numpy as np
from gesture_detector import GestureDetector
from drawing_canvas import DrawingCanvas


class VirtualDrawingApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to access webcam")
        
        h, w, _ = frame.shape
        
        self.detector = GestureDetector(smoothing_frames=5)
        self.canvas = DrawingCanvas(w, h)
        
        self.current_gesture = "NONE"
        self.prev_gesture = "NONE"
        
        # UI settings
        self.show_instructions = True
        
    def draw_ui(self, frame):
        """Draw UI elements on frame"""
        h, w, _ = frame.shape
        
        # Semi-transparent overlay for UI
        overlay = frame.copy()
        
        # Status bar
        cv2.rectangle(overlay, (0, 0), (w, 60), (50, 50, 50), -1)
        
        # Gesture status
        gesture_text = f"Gesture: {self.current_gesture}"
        cv2.putText(overlay, gesture_text, (10, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Color indicator
        color_pos = (w - 150, 30)
        cv2.circle(overlay, color_pos, 20, self.canvas.current_color, -1)
        cv2.putText(overlay, "Color", (w - 130, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Instructions
        if self.show_instructions:
            instructions = [
                "☝️  Index finger: Draw",
                "✊ Closed fist: Erase",
                "🤚 Open palm: Clear all",
                "✌️  Two fingers: Undo",
                "",
                "Keys: G/B/R/Y/W/P (colors)",
                "      S (save), Q (quit)",
                "      H (hide help)"
            ]
            
            y_offset = 100
            for instruction in instructions:
                cv2.putText(overlay, instruction, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                y_offset += 30
        
        # Blend overlay
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        return frame
    
    def run(self):
        """Main application loop"""
        print("🎨 Virtual Hand-Drawing App Started!")
        print("Press 'Q' to quit, 'S' to save, 'H' to toggle help")
        
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
                self.current_gesture = self.detector.detect_gesture(fingers_up)
                
                # Get index finger position (smoothed)
                finger_pos = self.detector.get_index_finger_tip(
                    landmarks, frame.shape
                )
                
                # Handle gestures
                if self.current_gesture == "DRAW":
                    if self.prev_gesture != "DRAW":
                        self.canvas.start_stroke()
                    self.canvas.draw(finger_pos)
                    # Draw visual indicator
                    cv2.circle(frame, finger_pos, 10, (0, 255, 0), -1)
                    
                elif self.current_gesture == "ERASE":
                    self.canvas.erase(finger_pos)
                    cv2.circle(frame, finger_pos, 30, (0, 0, 255), 2)
                    
                elif self.current_gesture == "CLEAR":
                    if self.prev_gesture != "CLEAR":
                        self.canvas.clear()
                    
                elif self.current_gesture == "UNDO":
                    if self.prev_gesture != "UNDO":
                        self.canvas.undo()
                
                else:
                    if self.prev_gesture == "DRAW":
                        self.canvas.end_stroke()
                
                # Draw hand landmarks
                frame = self.detector.draw_hand_landmarks(frame, results)
                
                self.prev_gesture = self.current_gesture
            else:
                self.current_gesture = "NONE"
                if self.prev_gesture == "DRAW":
                    self.canvas.end_stroke()
                self.prev_gesture = "NONE"
            
            # Composite: webcam + drawing canvas
            canvas_overlay = self.canvas.get_canvas()
            frame = cv2.addWeighted(frame, 0.7, canvas_overlay, 0.3, 0)
            
            # Draw UI
            frame = self.draw_ui(frame)
            
            # Display
            cv2.imshow("Virtual Hand-Drawing", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = self.canvas.save_canvas()
                print(f"✅ Saved: {filename}")
            elif key == ord('h'):
                self.show_instructions = not self.show_instructions
            else:
                # Color change keys
                if chr(key) in self.canvas.colors:
                    self.canvas.change_color(chr(key))
                    print(f"🎨 Color changed!")
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("👋 App closed!")


if __name__ == "__main__":
    app = VirtualDrawingApp()
    app.run()