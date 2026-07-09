"""Tracking module for Shanhai Spirit.

This module provides hand and face tracking functionality
using MediaPipe computer vision framework.
"""

import cv2
import mediapipe as mp
import numpy as np
from .config import (
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    GESTURE_NONE,
    GESTURE_SUMMON_ZHUQUE,
    GESTURE_SUMMON_YINGLONG,
    GESTURE_SUMMON_QILIN,
    GESTURE_SUMMON_XUANWU,
    MOUTH_OPEN_THRESHOLD,
    MOUTH_UPPER_LANDMARK,
    MOUTH_LOWER_LANDMARK,
)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh


class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self.hand_detected = False
        self.hand_coordinates = (0.5, 0.5)
        self.current_gesture = GESTURE_NONE
        self.finger_states = [False] * 5
        self.last_hand_coordinates = (0.5, 0.5)
        self.hand_speed = 0.0

    def detect_gesture(self, landmarks):
        if landmarks is None:
            return GESTURE_NONE

        finger_states = [False] * 5
        for i in range(5):
            if i == 0:
                finger_states[i] = landmarks[4].x < landmarks[3].x
            else:
                finger_states[i] = landmarks[i * 4 + 3].y < landmarks[i * 4].y

        if finger_states == [True, True, True, True, True]:
            return GESTURE_SUMMON_ZHUQUE
        elif finger_states == [False, True, True, False, False]:
            return GESTURE_SUMMON_YINGLONG
        elif finger_states == [False, True, True, True, False]:
            return GESTURE_SUMMON_QILIN
        elif finger_states == [False, False, False, False, False]:
            return GESTURE_SUMMON_XUANWU
        else:
            return GESTURE_NONE

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            x = landmarks[9].x
            y = landmarks[9].y

            self.hand_speed = np.sqrt(
                (x - self.last_hand_coordinates[0]) ** 2 +
                (y - self.last_hand_coordinates[1]) ** 2
            ) * 100

            self.last_hand_coordinates = (x, y)
            self.hand_coordinates = (x, y)
            self.hand_detected = True
            self.current_gesture = self.detect_gesture(landmarks)
            for i in range(5):
                if i == 0:
                    self.finger_states[i] = landmarks[4].x < landmarks[3].x
                else:
                    self.finger_states[i] = landmarks[i * 4 + 3].y < landmarks[i * 4].y

            return {
                "hand_detected": True,
                "hand_x": x,
                "hand_y": y,
                "hand_speed": self.hand_speed,
                "gesture": self.current_gesture,
                "landmarks": landmarks,
                "finger_states": self.finger_states,
            }
        else:
            self.hand_detected = False
            self.current_gesture = GESTURE_NONE
            return {
                "hand_detected": False,
                "hand_x": self.hand_coordinates[0],
                "hand_y": self.hand_coordinates[1],
                "hand_speed": 0.0,
                "gesture": GESTURE_NONE,
                "landmarks": None,
                "finger_states": [False] * 5,
            }

    def draw_hand(self, frame, landmarks):
        if landmarks:
            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            )
        return frame

    def get_tracking_result(self):
        return {
            "hand_detected": self.hand_detected,
            "hand_x": self.hand_coordinates[0],
            "hand_y": self.hand_coordinates[1],
            "hand_speed": self.hand_speed,
            "gesture": self.current_gesture,
            "finger_states": self.finger_states,
        }


class FaceTracker:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.face_detected = False
        self.mouth_open = False
        self.mouth_ratio = 0.0

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            upper_lip = landmarks[MOUTH_UPPER_LANDMARK]
            lower_lip = landmarks[MOUTH_LOWER_LANDMARK]

            self.mouth_ratio = abs(lower_lip.y - upper_lip.y)
            self.mouth_open = self.mouth_ratio > MOUTH_OPEN_THRESHOLD
            self.face_detected = True

            return {
                "face_detected": True,
                "mouth_open": self.mouth_open,
                "mouth_ratio": self.mouth_ratio,
            }
        else:
            self.face_detected = False
            self.mouth_open = False
            self.mouth_ratio = 0.0

            return {
                "face_detected": False,
                "mouth_open": False,
                "mouth_ratio": 0.0,
            }

    def get_tracking_result(self):
        return {
            "face_detected": self.face_detected,
            "mouth_open": self.mouth_open,
            "mouth_ratio": self.mouth_ratio,
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
            "face": face_result,
        }

    def draw_landmarks(self, frame):
        hand_result = self.hand_tracker.process_frame(frame)
        if hand_result["landmarks"]:
            frame = self.hand_tracker.draw_hand(frame, hand_result["landmarks"])
        return frame

    def get_hand_tracker(self):
        return self.hand_tracker

    def get_face_tracker(self):
        return self.face_tracker
