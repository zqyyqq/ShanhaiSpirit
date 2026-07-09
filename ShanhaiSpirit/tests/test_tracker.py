"""Tests for tracker module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from shanhai.tracker import HandTracker, FaceTracker, CombinedTracker


class TestHandTracker:
    def test_initialization(self):
        tracker = HandTracker()
        assert not tracker.hand_detected
        assert tracker.hand_coordinates == (0.5, 0.5)
        assert tracker.current_gesture == 0
        assert len(tracker.finger_states) == 5

    def test_get_tracking_result(self):
        tracker = HandTracker()
        result = tracker.get_tracking_result()

        assert "hand_detected" in result
        assert "hand_x" in result
        assert "hand_y" in result
        assert "gesture" in result
        assert "finger_states" in result

        assert isinstance(result["hand_detected"], bool)
        assert isinstance(result["hand_x"], float)
        assert isinstance(result["hand_y"], float)
        assert isinstance(result["gesture"], int)


class TestFaceTracker:
    def test_initialization(self):
        tracker = FaceTracker()
        assert not tracker.face_detected
        assert not tracker.mouth_open
        assert tracker.mouth_ratio == 0.0

    def test_get_tracking_result(self):
        tracker = FaceTracker()
        result = tracker.get_tracking_result()

        assert "face_detected" in result
        assert "mouth_open" in result
        assert "mouth_ratio" in result

        assert isinstance(result["face_detected"], bool)
        assert isinstance(result["mouth_open"], bool)
        assert isinstance(result["mouth_ratio"], float)


class TestCombinedTracker:
    def test_initialization(self):
        tracker = CombinedTracker()
        assert tracker.hand_tracker is not None
        assert tracker.face_tracker is not None

    def test_get_hand_tracker(self):
        tracker = CombinedTracker()
        assert isinstance(tracker.get_hand_tracker(), HandTracker)

    def test_get_face_tracker(self):
        tracker = CombinedTracker()
        assert isinstance(tracker.get_face_tracker(), FaceTracker)

    def test_process_frame_structure(self):
        tracker = CombinedTracker()
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        with patch.object(tracker.hand_tracker, "process_frame") as mock_hand:
            with patch.object(tracker.face_tracker, "process_frame") as mock_face:
                mock_hand.return_value = {
                    "hand_detected": True,
                    "hand_x": 0.5,
                    "hand_y": 0.5,
                    "hand_speed": 0.0,
                    "gesture": 1,
                    "landmarks": None,
                    "finger_states": [False, True, False, False, False],
                }
                mock_face.return_value = {
                    "face_detected": False,
                    "mouth_open": False,
                    "mouth_ratio": 0.0,
                }

                result = tracker.process_frame(mock_frame)

                assert "hand" in result
                assert "face" in result
                mock_hand.assert_called_once()
                mock_face.assert_called_once()
