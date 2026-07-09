"""Creature module for Shanhai Spirit.

This module handles creature rendering, management, and interaction
with the tracking system.
"""

import cv2
import os
import glob
import time
from .config import (
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CREATURE_SIZE,
    CREATURE_SPEED_FACTOR,
    CREATURES_DATA,
    GESTURE_COOLDOWN_MS,
    CREATURES_DIR,
)


class CreatureRenderer:
    def __init__(self, creature_id):
        self.creature_id = creature_id
        self.x = 0.5
        self.y = 0.5
        self.target_x = 0.5
        self.target_y = 0.5
        self.frames = []
        self.current_frame = 0
        self.last_frame_time = 0
        self.frame_rate = 15
        self.opacity = 0.0
        self.max_opacity = 0.85
        self.load_frames()

    def load_frames(self):
        pattern = os.path.join(CREATURES_DIR, self.creature_id, "*.png")
        frame_files = sorted(glob.glob(pattern))
        self.frames = [cv2.imread(f, cv2.IMREAD_UNCHANGED) for f in frame_files if cv2.imread(f, cv2.IMREAD_UNCHANGED) is not None]

    def is_valid(self):
        return len(self.frames) > 0

    def update(self, target_x, target_y, speed=0.0, mouth_open=False):
        self.target_x = target_x
        self.target_y = target_y

        self.x += (self.target_x - self.x) * CREATURE_SPEED_FACTOR
        self.y += (self.target_y - self.y) * CREATURE_SPEED_FACTOR

        if mouth_open:
            self.opacity = min(self.max_opacity, self.opacity + 0.05)
        else:
            self.opacity = max(0.5, self.opacity - 0.02)

        if self.frames:
            current_time = time.time() * 1000
            if current_time - self.last_frame_time > 1000 / self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_frame_time = current_time

    def draw(self, frame):
        if not self.frames or self.opacity <= 0:
            return frame

        creature_frame = self.frames[self.current_frame]
        if creature_frame is None:
            return frame

        creature_height, creature_width = creature_frame.shape[:2]
        target_width = int(CAMERA_WIDTH * CREATURE_SIZE)
        target_height = int(creature_height * (target_width / creature_width))
        resized_frame = cv2.resize(creature_frame, (target_width, target_height))

        x_pos = int(self.x * (CAMERA_WIDTH - target_width))
        y_pos = int(self.y * (CAMERA_HEIGHT - target_height))

        if resized_frame.shape[2] == 4:
            alpha_channel = resized_frame[:, :, 3] / 255.0
            for c in range(3):
                frame[y_pos:y_pos+target_height, x_pos:x_pos+target_width, c] = (
                    frame[y_pos:y_pos+target_height, x_pos:x_pos+target_width, c] * (1 - alpha_channel * self.opacity) +
                    resized_frame[:, :, c] * (alpha_channel * self.opacity)
                )
        else:
            frame[y_pos:y_pos+target_height, x_pos:x_pos+target_width] = resized_frame

        return frame

    def get_position(self):
        return self.x, self.y


class CreatureManager:
    def __init__(self):
        self.active_creature = None
        self.creature_data = None
        self.last_summon_time = 0

    def summon_creature(self, gesture_id):
        if gesture_id not in CREATURES_DATA:
            return False

        current_time = time.time() * 1000
        if current_time - self.last_summon_time < GESTURE_COOLDOWN_MS:
            return False

        creature_info = CREATURES_DATA[gesture_id]
        renderer = CreatureRenderer(creature_info["id"])

        if not renderer.is_valid():
            return False

        self.active_creature = renderer
        self.creature_data = creature_info
        self.last_summon_time = current_time

        return True

    def update_creature(self, hand_x, hand_y, speed=0.0, mouth_open=False):
        if self.active_creature:
            self.active_creature.update(hand_x, hand_y, speed, mouth_open)

    def draw_creature(self, frame):
        if self.active_creature:
            return self.active_creature.draw(frame)
        return frame

    def get_creature_info(self):
        return self.creature_data

    def has_active_creature(self):
        return self.active_creature is not None

    def get_creature_position(self):
        if self.active_creature:
            return self.active_creature.get_position()
        return (0.5, 0.5)

    def clear_creature(self):
        self.active_creature = None
        self.creature_data = None
