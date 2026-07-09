"""Configuration module for Shanhai Spirit.

This module defines all configuration constants and data structures
for the interactive art installation.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKGROUND_DIR = os.path.join(ASSETS_DIR, "backgrounds")
CREATURES_DIR = os.path.join(ASSETS_DIR, "creatures")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

RENDER_WIDTH = 1280
RENDER_HEIGHT = 720

MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

GESTURE_NONE = 0
GESTURE_SUMMON_ZHUQUE = 1
GESTURE_SUMMON_YINGLONG = 2
GESTURE_SUMMON_QILIN = 3
GESTURE_SUMMON_XUANWU = 4

GESTURE_MAP = {
    GESTURE_NONE: "无手势",
    GESTURE_SUMMON_ZHUQUE: "召唤朱雀",
    GESTURE_SUMMON_YINGLONG: "召唤应龙",
    GESTURE_SUMMON_QILIN: "召唤麒麟",
    GESTURE_SUMMON_XUANWU: "召唤玄武",
}

MOUTH_OPEN_THRESHOLD = 0.03
MOUTH_UPPER_LANDMARK = 13
MOUTH_LOWER_LANDMARK = 14

CREATURE_SIZE = 0.35
CREATURE_SPEED_FACTOR = 0.08
GESTURE_COOLDOWN_MS = 3000

BACKGROUNDS = [
    {"name": "北冥", "id": "beiming", "description": "北冥有鱼，其名为鲲"},
    {"name": "昆仑", "id": "kunlun", "description": "昆仑之墟，方八百里"},
    {"name": "沧海", "id": "canghai", "description": "东临碣石，以观沧海"},
]

CREATURES_DATA = {
    1: {"name": "朱雀", "id": "zhuque", "description": "南方神兽，浴火重生", "source": "山海经", "element": "火", "direction": "南"},
    2: {"name": "应龙", "id": "yinglong", "description": "有翼之龙，兴云致雨", "source": "山海经", "element": "水", "direction": "中"},
    3: {"name": "麒麟", "id": "qilin", "description": "瑞兽之王，太平之象", "source": "山海经", "element": "土", "direction": "东"},
    4: {"name": "玄武", "id": "xuanwu", "description": "北方神兽，龟蛇合体", "source": "山海经", "element": "水", "direction": "北"},
}
