"""Tests for creature module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from shanhai.creature import CreatureRenderer, CreatureManager
from shanhai.config import CREATURES_DATA, CREATURE_SPEED_FACTOR


class TestCreatureRenderer:
    def test_initialization(self):
        renderer = CreatureRenderer("zhuque")
        assert renderer.creature_id == "zhuque"
        assert renderer.x == 0.5
        assert renderer.y == 0.5
        assert renderer.target_x == 0.5
        assert renderer.target_y == 0.5

    def test_update_position(self):
        renderer = CreatureRenderer("zhuque")
        renderer.x = 0.0
        renderer.y = 0.0

        renderer.update(1.0, 1.0, 0.5, False)

        expected_x = 0.0 + (1.0 - 0.0) * CREATURE_SPEED_FACTOR
        expected_y = 0.0 + (1.0 - 0.0) * CREATURE_SPEED_FACTOR

        assert renderer.x == pytest.approx(expected_x)
        assert renderer.y == pytest.approx(expected_y)
        assert renderer.target_x == 1.0
        assert renderer.target_y == 1.0

    def test_get_position(self):
        renderer = CreatureRenderer("zhuque")
        renderer.x = 0.3
        renderer.y = 0.7

        x, y = renderer.get_position()
        assert x == 0.3
        assert y == 0.7


class TestCreatureManager:
    def test_initialization(self):
        manager = CreatureManager()
        assert manager.active_creature is None
        assert manager.creature_data is None
        assert manager.last_summon_time == 0

    def test_summon_creature_success(self):
        manager = CreatureManager()

        result = manager.summon_creature(1)

        assert result is True
        assert manager.active_creature is not None
        assert manager.creature_data == CREATURES_DATA[1]
        assert manager.creature_data["name"] == "朱雀"

    def test_summon_creature_invalid_id(self):
        manager = CreatureManager()

        result = manager.summon_creature(999)

        assert result is False
        assert manager.active_creature is None
        assert manager.creature_data is None

    def test_summon_creature_cooldown(self):
        manager = CreatureManager()
        manager.summon_creature(1)
        first_summon_time = manager.last_summon_time

        result = manager.summon_creature(2)

        assert result is False
        assert manager.last_summon_time == first_summon_time

    def test_has_active_creature(self):
        manager = CreatureManager()

        assert manager.has_active_creature() is False

        manager.summon_creature(1)

        assert manager.has_active_creature() is True

    def test_get_creature_info(self):
        manager = CreatureManager()

        assert manager.get_creature_info() is None

        manager.summon_creature(3)

        info = manager.get_creature_info()
        assert info is not None
        assert info["name"] == "麒麟"

    def test_get_creature_position(self):
        manager = CreatureManager()

        x, y = manager.get_creature_position()
        assert x == 0.5
        assert y == 0.5

        manager.summon_creature(1)
        x, y = manager.get_creature_position()
        assert x == 0.5
        assert y == 0.5

    def test_clear_creature(self):
        manager = CreatureManager()
        manager.summon_creature(1)

        assert manager.has_active_creature() is True

        manager.clear_creature()

        assert manager.has_active_creature() is False
        assert manager.get_creature_info() is None
