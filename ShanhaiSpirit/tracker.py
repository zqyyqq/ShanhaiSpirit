import cv2
import mediapipe as mp
import time
import numpy as np
from config import *


class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.hand_detected = False
        self.hand_coordinates = (0.5, 0.5)
        self.current_gesture = 0
        self.last_gesture_change = 0
        self.last_action_time = 0
        self.finger_states = [False] * 5

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        self.hand_detected = False
        self.current_gesture = 0
        
        if results.multi_hand_landmarks:
            self.hand_detected = True
            landmarks = results.multi_hand_landmarks[0]
            
            wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            self.hand_coordinates = (wrist.x, wrist.y)
            
            self._update_finger_states(landmarks)
            extended_fingers = sum(self.finger_states)
            
            if extended_fingers == 5:
                self.current_gesture = 0
            elif 1 <= extended_fingers <= 4:
                self.current_gesture = extended_fingers
        
        return self._get_tracking_result()

    def _update_finger_states(self, landmarks):
        for i in range(5):
            if i == 0:
                tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                ip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
                mcp = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_MCP]
                self.finger_states[i] = abs(tip.x - mcp.x) > abs(ip.x - mcp.x) * 1.2
            else:
                tip = landmarks.landmark[self.mp_hands.HandLandmark(i * 4 + 4)]
                pip = landmarks.landmark[self.mp_hands.HandLandmark(i * 4 + 2)]
                self.finger_states[i] = tip.y < pip.y

    def _get_tracking_result(self):
        return {
            "hand_detected": self.hand_detected,
            "hand_x": self.hand_coordinates[0],
            "hand_y": self.hand_coordinates[1],
            "hand_speed": 0.0,
            "gesture": self.current_gesture,
            "landmarks": None
        }


class FaceTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.face_detected = False
        self.mouth_open = False

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        self.face_detected = False
        self.mouth_open = False
        
        if results.multi_face_landmarks:
            self.face_detected = True
            landmarks = results.multi_face_landmarks[0].landmark
            
            upper_lip = landmarks[13]
            lower_lip = landmarks[14]
            
            mouth_dist = np.sqrt(
                (upper_lip.x - lower_lip.x) ** 2 +
                (upper_lip.y - lower_lip.y) ** 2
            )
            
            self.mouth_open = mouth_dist > 0.02
        
        return self._get_tracking_result()

    def _get_tracking_result(self):
        return {
            "face_detected": self.face_detected,
            "mouth_open": self.mouth_open,
            "mouth_ratio": 0.0
        }


class CombinedTracker:
    def __init__(self):
        self.hand_tracker = HandTracker()
        self.face_tracker = FaceTracker()

    def process_frame(self, frame):
        hand_result = self.hand_tracker.process_frame(frame)
        face_result = self.face_tracker.process_frame(frame)
        
        return {
            "hand": hand_result,
            "face": face_result
        }