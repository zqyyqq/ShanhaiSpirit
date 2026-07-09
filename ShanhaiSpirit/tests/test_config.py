"""Tests for configuration module."""

import pytest
from shanhai.config import (
    BASE_DIR,
    ASSETS_DIR,
    BACKGROUND_DIR,
    CREATURES_DIR,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    CREATURE_SIZE,
    CREATURE_SPEED_FACTOR,
    RENDER_WIDTH,
    RENDER_HEIGHT,
    BACKGROUNDS,
    CREATURES_DATA,
    GESTURE_NONE,
    GESTURE_SUMMON_ZHUQUE,
    GESTURE_SUMMON_YINGLONG,
    GESTURE_SUMMON_QILIN,
    GESTURE_SUMMON_XUANWU,
    GESTURE_MAP,
    MOUTH_OPEN_THRESHOLD,
    MOUTH_UPPER_LANDMARK,
    MOUTH_LOWER_LANDMARK,
)


class TestPathsConfig:
    def test_base_dir_exists(self):
        import os

        assert os.path.exists(BASE_DIR)

    def test_assets_dir_exists(self):
        import os

        assert os.path.exists(ASSETS_DIR)

    def test_background_dir_exists(self):
        import os

        assert os.path.exists(BACKGROUND_DIR)

    def test_creatures_dir_exists(self):
        import os

        assert os.path.exists(CREATURES_DIR)


class TestCameraConfig:
    def test_camera_config(self):
        assert isinstance(CAMERA_INDEX, int)
        assert isinstance(CAMERA_WIDTH, int)
        assert isinstance(CAMERA_HEIGHT, int)
        assert CAMERA_WIDTH > 0
        assert CAMERA_HEIGHT > 0


class TestTrackingConfig:
    def test_tracking_config(self):
        assert 0 <= MIN_DETECTION_CONFIDENCE <= 1
        assert 0 <= MIN_TRACKING_CONFIDENCE <= 1


class TestCreatureConfig:
    def test_creature_config(self):
        assert CREATURE_SIZE > 0
        assert 0 < CREATURE_SPEED_FACTOR <= 1


class TestRenderConfig:
    def test_render_config(self):
        assert RENDER_WIDTH > 0
        assert RENDER_HEIGHT > 0


class TestBackgroundConfig:
    def test_backgrounds_config(self):
        assert isinstance(BACKGROUNDS, list)
        assert len(BACKGROUNDS) == 3

        for bg in BACKGROUNDS:
            assert "name" in bg
            assert "id" in bg
            assert "description" in bg


class TestCreaturesDataConfig:
    def test_creatures_data_config(self):
        assert isinstance(CREATURES_DATA, dict)
        assert len(CREATURES_DATA) == 4

        for key in range(1, 5):
            assert key in CREATURES_DATA
            creature_info = CREATURES_DATA[key]
            assert "name" in creature_info
            assert "id" in creature_info
            assert "description" in creature_info
            assert "source" in creature_info
            assert "element" in creature_info
            assert "direction" in creature_info


class TestGestureConfig:
    def test_gesture_config(self):
        assert GESTURE_NONE == 0
        assert GESTURE_SUMMON_ZHUQUE == 1
        assert GESTURE_SUMMON_YINGLONG == 2
        assert GESTURE_SUMMON_QILIN == 3
        assert GESTURE_SUMMON_XUANWU == 4

        assert isinstance(GESTURE_MAP, dict)
        assert len(GESTURE_MAP) == 5


class TestFaceConfig:
    def test_face_config(self):
        assert MOUTH_OPEN_THRESHOLD > 0
        assert isinstance(MOUTH_UPPER_LANDMARK, int)
        assert isinstance(MOUTH_LOWER_LANDMARK, int)
