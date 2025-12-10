import cv2
import mediapipe as mp
from collections import deque
import numpy as np
import math


class GestureDetector:
    def __init__(self, smoothing_frames=5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Smoothing buffer
        self.smoothing_frames = smoothing_frames
        self.position_buffer = deque(maxlen=smoothing_frames)
        
        # Custom gesture templates
        self.custom_gestures = {}
        self.gesture_sequence = deque(maxlen=10)
        
    def detect_hands(self, frame):
        """Detect hands in frame and return landmarks"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results
    
    def get_finger_states(self, landmarks):
        """
        Return which fingers are up [thumb, index, middle, ring, pinky]
        Returns: list of 1s and 0s
        """
        finger_tips = [4, 8, 12, 16, 20]  # Landmark IDs for fingertips
        finger_pips = [3, 6, 10, 14, 18]  # Landmark IDs below tips
        
        fingers_up = []
        
        # Thumb (special case - check x-coordinate)
        if landmarks[finger_tips[0]].x < landmarks[finger_pips[0]].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
            
        # Other fingers (check y-coordinate)
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
                
        return fingers_up
    
    def detect_gesture(self, fingers_up):
        """
        Detect gesture based on finger states
        Returns: gesture_name (str)
        """
        # Check custom gestures first
        finger_pattern = tuple(fingers_up)
        if finger_pattern in self.custom_gestures:
            return self.custom_gestures[finger_pattern]
        
        # Default gestures
        if fingers_up == [0, 1, 0, 0, 0]:
            return "DRAW"
        elif fingers_up == [0, 0, 0, 0, 0]:
            return "ERASE"
        elif fingers_up == [1, 1, 1, 1, 1]:
            return "CLEAR"
        elif fingers_up == [0, 1, 1, 0, 0]:
            return "UNDO"
        elif fingers_up == [1, 1, 0, 0, 0]:
            return "PINCH"  # For thickness control
        elif fingers_up == [0, 1, 1, 1, 0]:
            return "THREE_FINGERS"  # For brush shape change
        else:
            return "NONE"
    
    def get_pinch_distance(self, landmarks, frame_shape):
        """Calculate distance between thumb and index finger for thickness control"""
        h, w, _ = frame_shape
        
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
        index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
        
        distance = math.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
        return distance, (thumb_x, thumb_y), (index_x, index_y)
    
    def get_index_finger_tip(self, landmarks, frame_shape):
        """Get smoothed index finger tip position"""
        h, w, _ = frame_shape
        index_tip = landmarks[8]  # Index finger tip landmark
        
        x = int(index_tip.x * w)
        y = int(index_tip.y * h)
        
        # Add to smoothing buffer
        self.position_buffer.append((x, y))
        
        # Calculate smoothed position
        if len(self.position_buffer) > 0:
            smooth_x = int(np.mean([pos[0] for pos in self.position_buffer]))
            smooth_y = int(np.mean([pos[1] for pos in self.position_buffer]))
            return (smooth_x, smooth_y)
        
        return (x, y)
    
    def add_custom_gesture(self, name, finger_pattern):
        """Add custom gesture template"""
        self.custom_gestures[tuple(finger_pattern)] = name
    
    def detect_sequence_gesture(self, current_pos):
        """Detect sequence gestures like swirls, zigzags"""
        self.gesture_sequence.append(current_pos)
        
        if len(self.gesture_sequence) < 5:
            return "NONE"
        
        # Detect circular motion (swirl)
        if self._is_circular_motion():
            return "SWIRL"
        
        # Detect zigzag pattern
        if self._is_zigzag_motion():
            return "ZIGZAG"
        
        return "NONE"
    
    def _is_circular_motion(self):
        """Check if recent positions form a circular pattern"""
        if len(self.gesture_sequence) < 8:
            return False
        
        points = list(self.gesture_sequence)[-8:]
        
        # Calculate center
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)
        
        # Calculate angles
        angles = []
        for p in points:
            angle = math.atan2(p[1] - center_y, p[0] - center_x)
            angles.append(angle)
        
        # Check if angles span more than 270 degrees (3/4 circle)
        angle_range = max(angles) - min(angles)
        return angle_range > (3 * math.pi / 2)
    
    def _is_zigzag_motion(self):
        """Check if recent positions form a zigzag pattern"""
        if len(self.gesture_sequence) < 6:
            return False
        
        points = list(self.gesture_sequence)[-6:]
        
        # Check for alternating direction changes
        direction_changes = 0
        for i in range(len(points) - 2):
            dx1 = points[i+1][0] - points[i][0]
            dx2 = points[i+2][0] - points[i+1][0]
            
            if dx1 * dx2 < 0:  # Sign change indicates direction change
                direction_changes += 1
        
        return direction_changes >= 2
    
    def draw_hand_landmarks(self, frame, results):
        """Draw hand landmarks on frame"""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        return frame