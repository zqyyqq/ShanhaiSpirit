import os

# -------------------------- 项目路径配置 --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKGROUND_DIR = os.path.join(ASSETS_DIR, "backgrounds")
CREATURES_DIR = os.path.join(ASSETS_DIR, "creatures")

# -------------------------- 摄像头配置 --------------------------
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# -------------------------- MediaPipe 追踪配置 --------------------------
TRACK_FRAME_SKIP = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# -------------------------- 手势识别阈值 --------------------------
# 手指伸直阈值（手指关节角度判断）
FINGER_EXTENDED_THRESHOLD = 0.9
# 手掌张开阈值
PALM_OPEN_THRESHOLD = 0.85

# -------------------------- 手势状态机配置 --------------------------
GESTURE_HOLD_FRAMES = 5
GESTURE_COOLDOWN_MS = 800

# -------------------------- 面部检测配置 --------------------------
# 嘴部开合阈值（归一化距离）
MOUTH_OPEN_THRESHOLD = 0.08
# 面部宽度归一化参考点（left: 234, right: 454）
FACE_LEFT_LANDMARK = 234
FACE_RIGHT_LANDMARK = 454
# 嘴唇关键点（上: 13, 下: 14）
MOUTH_UPPER_LANDMARK = 13
MOUTH_LOWER_LANDMARK = 14

# -------------------------- 神兽配置 --------------------------
CREATURE_SIZE = 350
CREATURE_SPEED_FACTOR = 0.3

# 手部移动速度阈值（区分静止/行走）
MOVEMENT_THRESHOLD = 3.0

# 动画参数
IDLE_TAIL_SWING_SPEED = 0.02
IDLE_LIMB_WOBBLE_SPEED = 0.03
WALKING_TAIL_SWING_SPEED = 0.08
WALKING_LIMB_SPEED = 0.12

# -------------------------- 渲染配置 --------------------------
RENDER_WIDTH = 1920
RENDER_HEIGHT = 1080

# 国风颜色配置 - 青绿山水色调
COLOR_BACKGROUND_BASE = (245, 240, 230)
COLOR_GREEN_DARK = (30, 80, 50)
COLOR_GREEN_LIGHT = (80, 140, 100)
COLOR_BLUE_DARK = (30, 60, 100)
COLOR_BLUE_LIGHT = (80, 120, 180)
COLOR_INK_BLACK = (20, 20, 25)
COLOR_PAPER_BG = (252, 248, 242)
COLOR_TEXT_BORDER = (100, 80, 60)
COLOR_TEXT_FILL = (40, 35, 30)

# -------------------------- 背景配置 --------------------------
BACKGROUNDS = [
    {"name": "昆仑", "id": "kunlun"},
    {"name": "沙漠", "id": "desert"},
    {"name": "大海", "id": "sea"}
]

# -------------------------- 神兽数据 --------------------------
CREATURES_DATA = {
    1: {
        "name": "朱雀",
        "id": "zhuque",
        "description": "南方有鸟，其名曰朱雀，丹身而赤目，六足四翼，见则天下大旱。",
        "source": "《山海经·南次二经》"
    },
    2: {
        "name": "应龙",
        "id": "yinglong",
        "description": "应龙处南极，杀蚩尤与夸父，不得复上，故下数旱。旱而为应龙之状，乃得大雨。",
        "source": "《山海经·大荒东经》"
    },
    3: {
        "name": "麒麟",
        "id": "qilin",
        "description": "麟，仁兽也。麇身牛尾，狼额马蹄，有五彩，腹下黄，高丈二。",
        "source": "《山海经·海内经》"
    },
    4: {
        "name": "玄武",
        "id": "xuanwu",
        "description": "北方有神龟，其名曰玄武，龟蛇相缠，能通幽冥，知未来之事。",
        "source": "《山海经·北山经》"
    }
}