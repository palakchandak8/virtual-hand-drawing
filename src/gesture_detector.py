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
    
    def detect_gesture(self, fingers_up, landmarks=None, frame_shape=None):
        """
        Detect gesture based on finger states
        Returns: gesture_name (str)
        """
        # Check custom gestures first
        finger_pattern = tuple(fingers_up)
        if finger_pattern in self.custom_gestures:
            return self.custom_gestures[finger_pattern]
        
        # UPDATED GESTURES
        # Index finger only - DRAW (most important, check first)
        if fingers_up == [0, 1, 0, 0, 0]:
            # Additional check: make sure thumb and index are NOT too close (not pinching)
            if landmarks and frame_shape:
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                h, w, _ = frame_shape
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                distance = math.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
                
                # If distance is too small, it's likely a pinch, not draw
                if distance < 40:
                    return "NONE"
            return "DRAW"
        
        # Closed fist (all fingers down) - ERASE ALL
        elif fingers_up == [0, 0, 0, 0, 0]:
            return "ERASE_ALL"
        
        # Open palm (all fingers up) - PAUSE/VERIFY
        elif fingers_up == [1, 1, 1, 1, 1]:
            return "PAUSE"
        
        # Two fingers (index + middle) - UNDO
        elif fingers_up == [0, 1, 1, 0, 0]:
            return "UNDO"
        
        # Three fingers (index + middle + ring) - CHANGE BRUSH
        elif fingers_up == [0, 1, 1, 1, 0]:
            return "THREE_FINGERS"
        
        # Thumb + Index (both up, others down) - PINCH for thickness
        elif fingers_up == [1, 1, 0, 0, 0]:
            if landmarks and frame_shape:
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                h, w, _ = frame_shape
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                distance = math.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
                
                # Only consider it a pinch if fingers are relatively close
                if distance < 150:
                    return "PINCH"
            return "NONE"
        
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