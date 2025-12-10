import cv2
import time


class NotificationSystem:
    def __init__(self):
        self.notifications = []
        self.max_notifications = 5
        
    def add_notification(self, message, duration=2.0, type='info'):
        """
        Add a notification
        type: 'info', 'success', 'warning', 'error'
        """
        notification = {
            'message': message,
            'timestamp': time.time(),
            'duration': duration,
            'type': type,
            'alpha': 1.0
        }
        self.notifications.append(notification)
        
        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
    
    def draw(self, frame):
        """Draw all active notifications"""
        current_time = time.time()
        h, w, _ = frame.shape
        
        # Filter expired notifications
        self.notifications = [n for n in self.notifications 
                             if current_time - n['timestamp'] < n['duration']]
        
        y_offset = 140  # Start below ribbon
        
        for notification in self.notifications:
            elapsed = current_time - notification['timestamp']
            
            # Fade out in last 0.5 seconds
            if elapsed > notification['duration'] - 0.5:
                notification['alpha'] = (notification['duration'] - elapsed) / 0.5
            
            # Color based on type
            if notification['type'] == 'success':
                bg_color = (0, 180, 0)  # Green
            elif notification['type'] == 'error':
                bg_color = (0, 0, 200)  # Red
            elif notification['type'] == 'warning':
                bg_color = (0, 165, 255)  # Orange
            else:
                bg_color = (100, 100, 100)  # Gray
            
            # Calculate dimensions
            text_size = cv2.getTextSize(notification['message'], 
                                       cv2.FONT_HERSHEY_SIMPLEX, 
                                       0.6, 2)[0]
            box_width = text_size[0] + 40
            box_height = 50
            box_x = w - box_width - 20
            box_y = y_offset
            
            # Create overlay for transparency
            overlay = frame.copy()
            
            # Draw notification box
            cv2.rectangle(overlay,
                         (box_x, box_y),
                         (box_x + box_width, box_y + box_height),
                         bg_color,
                         -1)
            
            # Draw border
            cv2.rectangle(overlay,
                         (box_x, box_y),
                         (box_x + box_width, box_y + box_height),
                         (255, 255, 255),
                         2)
            
            # Apply transparency
            cv2.addWeighted(overlay, notification['alpha'] * 0.9, 
                          frame, 1 - (notification['alpha'] * 0.9), 0, frame)
            
            # Draw text
            text_x = box_x + 20
            text_y = box_y + 32
            cv2.putText(frame, notification['message'],
                       (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.6,
                       (255, 255, 255),
                       2)
            
            y_offset += box_height + 10
        
        return frame