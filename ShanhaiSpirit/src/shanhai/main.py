"""Main entry point for Shanhai Spirit.

《山海灵识》- 基于计算机视觉的实时体感交互艺术装置
"""

import cv2
import numpy as np
import time
import os
import logging

from tracker import CombinedTracker
from creature import CreatureManager
from config import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    RENDER_WIDTH,
    RENDER_HEIGHT,
    BACKGROUND_DIR,
    GESTURE_NONE,
    GESTURE_MAP,
    BACKGROUNDS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextRenderer:
    @staticmethod
    def put_text(frame, text, x, y, font_scale=1, color=(255, 255, 255), thickness=2, background=False):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

        if background:
            cv2.rectangle(frame, (x, y - text_size[1] - 5), (x + text_size[0], y + 5), (0, 0, 0), -1)

        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
        return frame


class BackgroundRenderer:
    def __init__(self):
        self.backgrounds = []
        self.current_background = 0
        self.last_switch_time = 0
        self.load_backgrounds()

    def load_backgrounds(self):
        for bg in BACKGROUNDS:
            bg_path = os.path.join(BACKGROUND_DIR, f"{bg['id']}.jpg")
            if os.path.exists(bg_path):
                bg_image = cv2.imread(bg_path)
                bg_image = cv2.resize(bg_image, (RENDER_WIDTH, RENDER_HEIGHT))
                self.backgrounds.append(bg_image)

    def get_current_background(self):
        if self.backgrounds:
            return self.backgrounds[self.current_background]
        return None

    def switch_background(self):
        if len(self.backgrounds) > 1:
            self.current_background = (self.current_background + 1) % len(self.backgrounds)

    def get_background_name(self):
        if self.backgrounds:
            return BACKGROUNDS[self.current_background]["name"]
        return "未知"


class InfoBoxRenderer:
    @staticmethod
    def draw_info_box(frame, creature_info, gesture, fps):
        if creature_info:
            box_y = RENDER_HEIGHT - 150
            cv2.rectangle(frame, (10, box_y), (400, RENDER_HEIGHT - 10), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, box_y), (400, RENDER_HEIGHT - 10), (255, 255, 255), 2)

            TextRenderer.put_text(frame, f"神兽: {creature_info['name']}", 25, box_y + 30)
            TextRenderer.put_text(frame, f"来源: {creature_info['source']}", 25, box_y + 60)
            TextRenderer.put_text(frame, f"属性: {creature_info['element']}", 25, box_y + 90)
            TextRenderer.put_text(frame, f"方位: {creature_info['direction']}", 25, box_y + 120)

        gesture_text = GESTURE_MAP.get(gesture, "未知手势")
        TextRenderer.put_text(frame, f"手势: {gesture_text}", 10, 30)
        TextRenderer.put_text(frame, f"FPS: {fps:.1f}", RENDER_WIDTH - 100, 30)

        return frame


class Application:
    def __init__(self):
        self.tracker = CombinedTracker()
        self.creature_manager = CreatureManager()
        self.background_renderer = BackgroundRenderer()
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.fps = 0.0

    def run(self):
        logger.info("启动《山海灵识》交互装置")
        logger.info("按 'q' 退出")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                self.fps = self.frame_count / (current_time - self.last_fps_time)
                self.frame_count = 0
                self.last_fps_time = current_time

            frame = cv2.flip(frame, 1)

            tracking_result = self.tracker.process_frame(frame)
            hand_result = tracking_result["hand"]
            face_result = tracking_result["face"]

            if hand_result["hand_detected"]:
                if hand_result["gesture"] != GESTURE_NONE:
                    self.creature_manager.summon_creature(hand_result["gesture"])
                else:
                    current_time_ms = time.time() * 1000
                    if current_time_ms - self.background_renderer.last_switch_time > 1000:
                        self.background_renderer.switch_background()
                        self.background_renderer.last_switch_time = current_time_ms

                self.creature_manager.update_creature(
                    hand_result["hand_x"],
                    hand_result["hand_y"],
                    hand_result["hand_speed"],
                    face_result["mouth_open"],
                )

            frame = self.creature_manager.draw_creature(frame)

            background = self.background_renderer.get_current_background()
            if background is not None:
                frame_resized = cv2.resize(frame, (RENDER_WIDTH, RENDER_HEIGHT))
                frame = cv2.addWeighted(frame_resized, 0.6, background, 0.4, 0)
            else:
                frame = cv2.resize(frame, (RENDER_WIDTH, RENDER_HEIGHT))

            frame = InfoBoxRenderer.draw_info_box(
                frame,
                self.creature_manager.get_creature_info(),
                hand_result["gesture"],
                self.fps,
            )

            cv2.imshow("Shanhai Spirit - 山海灵识", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("关闭《山海灵识》交互装置")


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
