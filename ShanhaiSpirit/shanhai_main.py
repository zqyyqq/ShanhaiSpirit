"""
《山海灵识》- SIGGRAPH 实时人机交互艺术作品
简化版主程序 - 直接使用OpenCV显示
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from tracker import (
    HandTracker,
    GESTURE_NONE,
    GESTURE_SUMMON_ZHUQUE,
    GESTURE_SUMMON_YINGLONG,
    GESTURE_SUMMON_QILIN,
    GESTURE_SUMMON_XUANWU,
    GESTURE_SWITCH_BACKGROUND,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKGROUND_DIR = os.path.join(ASSETS_DIR, "backgrounds")
CREATURES_DIR = os.path.join(ASSETS_DIR, "creatures")

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

CREATURES_DATA = {
    GESTURE_SUMMON_ZHUQUE: {
        "name": "朱雀",
        "id": "zhuque",
        "description": "《山海经·南次二经》云："
                       "南方有鸟，其名曰朱雀，"
                       "丹身而赤目，六足四翼，"
                       "见则天下大旱。",
    },
    GESTURE_SUMMON_YINGLONG: {
        "name": "应龙",
        "id": "yinglong",
        "description": "《山海经·大荒东经》云："
                       "应龙处南极，杀蚩尤与夸父，"
                       "不得复上，故下数旱。",
    },
    GESTURE_SUMMON_QILIN: {
        "name": "麒麟",
        "id": "qilin",
        "description": "《山海经·海内经》云："
                       "麟，仁兽也。麇身牛尾，"
                       "狼额马蹄，有五彩。",
    },
    GESTURE_SUMMON_XUANWU: {
        "name": "玄武",
        "id": "xuanwu",
        "description": "《山海经·北山经》云："
                       "北方有神龟，其名曰玄武，"
                       "龟蛇相缠，能通幽冥。",
    },
}

BACKGROUNDS = [
    {"name": "沧海", "id": "sea"},
    {"name": "沙漠", "id": "desert"},
    {"name": "昆仑", "id": "kunlun"},
]


def load_backgrounds():
    backgrounds = []
    for bg in BACKGROUNDS:
        bg_path = os.path.join(BACKGROUND_DIR, f"{bg['id']}.png")
        if os.path.exists(bg_path):
            img = cv2.imread(bg_path)
            img = cv2.resize(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            backgrounds.append(img)
    return backgrounds


def load_creatures():
    creatures = {}
    import glob
    for gesture_id, data in CREATURES_DATA.items():
        creature_dir = os.path.join(CREATURES_DIR, data["id"])
        if os.path.exists(creature_dir):
            pattern = os.path.join(creature_dir, "*.png")
            frame_files = sorted(glob.glob(pattern))
            frames = []
            for f in frame_files:
                img = cv2.imread(f, cv2.IMREAD_UNCHANGED)
                frames.append(img)
            creatures[data["id"]] = frames
    return creatures


def overlay_image(frame, img, x, y, size):
    img = cv2.resize(img, (size, size))
    
    if img.shape[2] == 4:
        b, g, r, a = cv2.split(img)
        overlay = cv2.merge((b, g, r))
        mask = a / 255.0
        
        y1 = max(0, y - size // 2)
        y2 = min(frame.shape[0], y + size // 2)
        x1 = max(0, x - size // 2)
        x2 = min(frame.shape[1], x + size // 2)
        
        img_y1 = max(0, size // 2 - y)
        img_y2 = img_y1 + (y2 - y1)
        img_x1 = max(0, size // 2 - x)
        img_x2 = img_x1 + (x2 - x1)
        
        frame[y1:y2, x1:x2] = (
            frame[y1:y2, x1:x2] * (1 - mask[img_y1:img_y2, img_x1:img_x2, np.newaxis]) +
            overlay[img_y1:img_y2, img_x1:img_x2] * mask[img_y1:img_y2, img_x1:img_x2, np.newaxis]
        )
    else:
        y1 = y - size // 2
        y2 = y + size // 2
        x1 = x - size // 2
        x2 = x + size // 2
        
        if y1 >= 0 and y2 < frame.shape[0] and x1 >= 0 and x2 < frame.shape[1]:
            frame[y1:y2, x1:x2] = cv2.resize(img, (size, size))
    
    return frame


def get_font(size):
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_chinese_text(frame, text, x, y, font_size=20, color=(0, 0, 0)):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = get_font(font_size)
    draw.text((x, y), text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def draw_text_box(frame, x, y, name, description):
    box_w = 320
    box_h = 170
    creature_size = int(WINDOW_WIDTH * 0.3)
    y1 = y + creature_size // 2 + 25
    x1 = x - box_w // 2
    
    if y1 + box_h > frame.shape[0]:
        y1 = frame.shape[0] - box_h - 15
    if x1 < 0:
        x1 = 10
    if x1 + box_w > frame.shape[1]:
        x1 = frame.shape[1] - box_w - 10
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x1 + box_w, y1 + box_h), (255, 248, 240), -1)
    cv2.addWeighted(overlay, 0.92, frame, 0.08, 0, frame)
    
    cv2.rectangle(frame, (x1, y1), (x1 + box_w, y1 + box_h), (100, 80, 60), 2)
    cv2.rectangle(frame, (x1 + 4, y1 + 4), (x1 + box_w - 4, y1 + box_h - 4), (150, 130, 100), 1)
    
    corner_size = 15
    corners = [
        (x1, y1), (x1 + box_w, y1),
        (x1, y1 + box_h), (x1 + box_w, y1 + box_h)
    ]
    for cx, cy in corners:
        cv2.line(frame, (cx, cy), (cx + corner_size, cy), (80, 60, 40), 2)
        cv2.line(frame, (cx, cy), (cx, cy + corner_size), (80, 60, 40), 2)
        cv2.line(frame, (cx + corner_size, cy), (cx + corner_size, cy + 5), (80, 60, 40), 1)
        cv2.line(frame, (cx + 5, cy + corner_size), (cx + corner_size, cy + corner_size), (80, 60, 40), 1)
    
    cv2.line(frame, (x1 + 20, y1 + 45), (x1 + box_w - 20, y1 + 45), (150, 130, 100), 1)
    
    font = get_font(28)
    name_w = font.getlength(name)
    frame = draw_chinese_text(frame, name, x1 + (box_w - name_w) // 2, y1 + 10, font_size=28, color=(60, 40, 20))
    
    frame = draw_chinese_text(frame, "《山海经》", x1 + (box_w - 80) // 2, y1 + 50, font_size=14, color=(120, 100, 80))
    
    lines = []
    current_line = ""
    for char in description:
        if len(current_line) >= 17:
            lines.append(current_line)
            current_line = ""
        current_line += char
    if current_line:
        lines.append(current_line)
    
    line_y = y1 + 75
    max_lines = 4
    display_lines = lines[:max_lines]
    
    for line in display_lines:
        font = get_font(16)
        line_w = font.getlength(line)
        frame = draw_chinese_text(frame, line, x1 + (box_w - line_w) // 2, line_y, font_size=16, color=(70, 60, 50))
        line_y += 24
    
    seal_x = x1 + box_w - 45
    seal_y = y1 + box_h - 45
    cv2.rectangle(frame, (seal_x, seal_y), (seal_x + 35, seal_y + 35), (180, 60, 60), 2)
    frame = draw_chinese_text(frame, "山海", seal_x + 5, seal_y + 8, font_size=16, color=(180, 60, 60))
    
    return frame


def draw_gesture_debug(frame, result):
    x = 10
    y = WINDOW_HEIGHT - 120
    
    cv2.rectangle(frame, (x, y), (x + 220, y + 100), (200, 200, 200), -1)
    cv2.rectangle(frame, (x, y), (x + 220, y + 100), (100, 100, 100), 2)
    
    frame = draw_chinese_text(frame, "手势检测状态", x + 10, y + 10, font_size=14, color=(50, 50, 50))
    
    finger_names = ["拇指", "食指", "中指", "无名指", "小指"]
    finger_states = result.get("finger_states", [False] * 5)
    
    for i, (name, state) in enumerate(zip(finger_names, finger_states)):
        status_text = "伸" if state else "屈"
        color = (0, 200, 0) if state else (200, 0, 0)
        text = f"{name}: {status_text}"
        frame = draw_chinese_text(frame, text, x + 10, y + 40 + i * 12, font_size=12, color=color)
    
    gesture_map = {
        0: "无",
        5: "切换背景",
        1: "朱雀",
        2: "应龙",
        3: "麒麟",
        4: "玄武",
    }
    gesture_name = gesture_map.get(result.get("gesture", 0), "未知")
    text = f"识别: {gesture_name}"
    frame = draw_chinese_text(frame, text, x + 10, y + 90, font_size=14, color=(0, 100, 200))
    
    return frame


def main():
    print("《山海灵识》启动")
    
    backgrounds = load_backgrounds()
    creatures = load_creatures()
    
    print(f"加载背景: {len(backgrounds)} 个")
    print(f"加载神兽: {len(creatures)} 个")
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    tracker = HandTracker()
    
    current_background = 0
    active_creature = None
    creature_info = None
    
    creature_x = WINDOW_WIDTH // 2
    creature_y = WINDOW_HEIGHT // 2
    target_x = WINDOW_WIDTH // 2
    target_y = WINDOW_HEIGHT // 2
    
    last_gesture_time = 0
    gesture_cooldown = 1500
    
    cv2.namedWindow("山海灵识", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("山海灵识", WINDOW_WIDTH, WINDOW_HEIGHT)
    
    while True:
        success, frame = cap.read()
        if not success:
            continue
        
        frame = cv2.flip(frame, 1)
        result = tracker.process_frame(frame)
        
        if result["hand_detected"]:
            target_x = int(result["hand_x"] * WINDOW_WIDTH)
            target_y = int(result["hand_y"] * WINDOW_HEIGHT)
            
            gesture = result["gesture"]
            if gesture != GESTURE_NONE:
                current_time = cv2.getTickCount() / cv2.getTickFrequency() * 1000
                if current_time - last_gesture_time > gesture_cooldown:
                    last_gesture_time = current_time
                    
                    if gesture == GESTURE_SWITCH_BACKGROUND:
                        current_background = (current_background + 1) % len(backgrounds)
                        print(f"切换背景: {BACKGROUNDS[current_background]['name']}")
                    elif gesture in CREATURES_DATA:
                        creature_info = CREATURES_DATA[gesture]
                        active_creature = creature_info["id"]
                        print(f"召唤神兽: {creature_info['name']}")
        
        creature_x += (target_x - creature_x) * 0.15
        creature_y += (target_y - creature_y) * 0.15
        
        if backgrounds:
            display_frame = backgrounds[current_background].copy()
        else:
            display_frame = np.full((WINDOW_HEIGHT, WINDOW_WIDTH, 3), 200, dtype=np.uint8)
        
        if active_creature and creature_info:
            frames = creatures.get(active_creature, [])
            if frames:
                img = frames[0]
                creature_size = int(WINDOW_WIDTH * 0.3)
                display_frame = overlay_image(display_frame, img, int(creature_x), int(creature_y), creature_size)
            
            display_frame = draw_text_box(display_frame, int(creature_x), int(creature_y),
                                         creature_info["name"], creature_info["description"])
        
        display_frame = draw_chinese_text(display_frame, "五指张开切换背景 | 1-4指召唤神兽 | Q退出",
                                          10, 15, font_size=14, color=(255, 255, 255))
        
        display_frame = draw_gesture_debug(display_frame, result)
        
        cv2.imshow("山海灵识", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("《山海灵识》关闭")


if __name__ == "__main__":
    main()
