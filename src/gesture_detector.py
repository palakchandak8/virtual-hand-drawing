import cv2
import mediapipe as mp
from collections import deque
import numpy as np


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
        if fingers_up == [0, 1, 0, 0, 0]:
            return "DRAW"
        elif fingers_up == [0, 0, 0, 0, 0]:
            return "ERASE"
        elif fingers_up == [1, 1, 1, 1, 1]:
            return "CLEAR"
        elif fingers_up == [0, 1, 1, 0, 0]:
            return "UNDO"
        else:
            return "NONE"
    
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