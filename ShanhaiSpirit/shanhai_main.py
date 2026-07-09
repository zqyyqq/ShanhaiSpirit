import cv2
import numpy as np
import os
import time
import sys
from tracker import CombinedTracker
from config import *

log_file = open(os.path.join(BASE_DIR, 'main_log.txt'), 'w')

def log(msg):
    log_file.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')
    log_file.flush()
    print(msg)

class CreatureRenderer:
    def __init__(self, creature_id):
        self.creature_id = creature_id
        self.creature_dir = os.path.join(CREATURES_DIR, creature_id)
        self.image_path = os.path.join(self.creature_dir, f"{creature_id}.png")
        
        if not os.path.exists(self.image_path):
            self.image_path = None
            log(f"警告: 未找到神兽图片 {self.image_path}")
        
        self.x = 0.5
        self.y = 0.5
        self.target_x = 0.5
        self.target_y = 0.5
        self.img = None
        
        if self.image_path:
            self.img = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
            if self.img is None:
                log(f"警告: 无法读取图片 {self.image_path}")
                self.image_path = None
            else:
                log(f"成功加载神兽图片: {self.image_path}, 尺寸: {self.img.shape}")
    
    def update(self, target_x, target_y, speed, mouth_open):
        self.target_x = target_x
        self.target_y = target_y
        
        self.x += (self.target_x - self.x) * CREATURE_SPEED_FACTOR
        self.y += (self.target_y - self.y) * CREATURE_SPEED_FACTOR
    
    def draw(self, frame):
        if self.img is None:
            return frame
        
        img_height, img_width = self.img.shape[:2]
        scale = CREATURE_SIZE / max(img_width, img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        resized = cv2.resize(self.img, (new_width, new_height))
        
        x_pos = int(self.x * frame.shape[1] - new_width / 2)
        y_pos = int(self.y * frame.shape[0] - new_height / 2)
        
        x_start = max(0, x_pos)
        y_start = max(0, y_pos)
        x_end = min(frame.shape[1], x_pos + new_width)
        y_end = min(frame.shape[0], y_pos + new_height)
        
        img_x_start = x_start - x_pos
        img_y_start = y_start - y_pos
        img_x_end = img_x_start + (x_end - x_start)
        img_y_end = img_y_start + (y_end - y_start)
        
        if resized.shape[2] == 4:
            alpha = resized[:, :, 3] / 255.0
            for c in range(3):
                frame[y_start:y_end, x_start:x_end, c] = (
                    frame[y_start:y_end, x_start:x_end, c] * (1 - alpha[img_y_start:img_y_end, img_x_start:img_x_end]) +
                    resized[img_y_start:img_y_end, img_x_start:img_x_end, c] * alpha[img_y_start:img_y_end, img_x_start:img_x_end]
                )
        else:
            frame[y_start:y_end, x_start:x_end] = resized[img_y_start:img_y_end, img_x_start:img_x_end]
        
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
            log(f"错误: 手势 {gesture_id} 不在神兽配置中")
            return False
        
        current_time = time.time() * 1000
        if current_time - self.last_summon_time < GESTURE_COOLDOWN_MS:
            return False
        
        creature_info = CREATURES_DATA[gesture_id]
        self.active_creature = CreatureRenderer(creature_info['id'])
        self.creature_data = creature_info
        self.last_summon_time = current_time
        log(f"召唤神兽: {creature_info['name']}")
        
        return True
    
    def update_creature(self, hand_x, hand_y, speed, mouth_open):
        if self.active_creature:
            self.active_creature.update(hand_x, hand_y, speed, mouth_open)
    
    def draw_creature(self, frame):
        if self.active_creature:
            return self.active_creature.draw(frame)
        return frame
    
    def get_creature_info(self):
        return self.creature_data

def cv2_put_text(img, text, pos, font_size=20, color=(0, 255, 0)):
    from PIL import Image, ImageDraw, ImageFont
    
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
        'C:/Windows/Fonts/msyhbd.ttc',
        'C:/Windows/Fonts/arial.ttf',
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, font_size)
            break
    
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    if font:
        draw.text(pos, text, font=font, fill=color)
    else:
        draw.text(pos, text, fill=color)
    
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def draw_creature_info(frame, creature_data, creature_x, creature_y):
    from PIL import Image, ImageDraw, ImageFont
    
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
    ]
    
    font = None
    font_size = 18
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, font_size)
            break
    
    info_box_width = 320
    info_box_height = 160
    info_box_x = int(creature_x * frame.shape[1])
    info_box_y = int(creature_y * frame.shape[0]) + CREATURE_SIZE // 2 + 20
    
    if info_box_x + info_box_width > frame.shape[1]:
        info_box_x = frame.shape[1] - info_box_width - 20
    if info_box_x < 20:
        info_box_x = 20
    if info_box_y + info_box_height > frame.shape[0]:
        info_box_y = frame.shape[0] - info_box_height - 20
    
    roi = frame[info_box_y:info_box_y+info_box_height, info_box_x:info_box_x+info_box_width]
    overlay = np.full_like(roi, (20, 20, 30), dtype=np.uint8)
    blended_roi = cv2.addWeighted(roi, 0.25, overlay, 0.75, 0)
    frame[info_box_y:info_box_y+info_box_height, info_box_x:info_box_x+info_box_width] = blended_roi
    
    cv2.rectangle(frame, (info_box_x, info_box_y), 
                  (info_box_x + info_box_width, info_box_y + info_box_height), 
                  (180, 160, 140), 2)
    
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    line_height = font_size + 4
    current_y = info_box_y + 20
    
    name_text = f"【{creature_data['name']}】"
    if font:
        draw.text((info_box_x + 15, current_y), name_text, font=font, fill=(255, 220, 180))
    else:
        draw.text((info_box_x + 15, current_y), name_text, fill=(255, 220, 180))
    current_y += line_height
    
    description = creature_data['description']
    max_chars_per_line = 17
    lines = []
    while len(description) > max_chars_per_line:
        lines.append(description[:max_chars_per_line])
        description = description[max_chars_per_line:]
    lines.append(description)
    
    for line in lines:
        if font:
            draw.text((info_box_x + 15, current_y), line, font=font, fill=(240, 235, 225))
        else:
            draw.text((info_box_x + 15, current_y), line, fill=(240, 235, 225))
        current_y += line_height
    
    source_text = f"—— {creature_data['source']}"
    if font:
        draw.text((info_box_x + 15, current_y), source_text, font=font, fill=(200, 180, 160))
    else:
        draw.text((info_box_x + 15, current_y), source_text, fill=(200, 180, 160))
    
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def main():
    log("=" * 50)
    log("初始化山海灵识...")
    log("=" * 50)
    
    log("1. 创建追踪器...")
    tracker = CombinedTracker()
    log("   追踪器创建成功")
    
    log("2. 创建神兽管理器...")
    creature_manager = CreatureManager()
    log("   神兽管理器创建成功")
    
    log("3. 打开摄像头...")
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    if not cap.isOpened():
        log("   DSHOW失败，尝试默认后端...")
        cap.release()
        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    if not cap.isOpened():
        log("ERROR: 无法打开摄像头！")
        log_file.close()
        return
    
    log("   摄像头打开成功！")
    
    current_background_index = 0
    last_background_switch = 0
    last_creature_summon = 0
    last_gesture = -1
    
    fps_count = 0
    fps_timer = time.time()
    current_fps = 0.0
    
    log("4. 创建窗口...")
    cv2.namedWindow('山海灵识', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('山海灵识', RENDER_WIDTH, RENDER_HEIGHT)
    log("   窗口创建成功")
    
    log("=" * 50)
    log("开始主循环...")
    log("=" * 50)
    
    debug_counter = 0
    
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            log("警告: 无法读取帧")
            time.sleep(0.01)
            continue
        
        frame = cv2.flip(frame, 1)
        
        tracking_data = tracker.process_frame(frame)
        
        hand_data = tracking_data["hand"]
        gesture = hand_data["gesture"]
        current_time = time.time() * 1000
        
        debug_counter += 1
        if debug_counter % 30 == 0:
            log(f"[调试] 手检测: {hand_data['hand_detected']}, 手势: {gesture}, 位置: ({hand_data['hand_x']:.2f}, {hand_data['hand_y']:.2f})")
        
        if gesture == 0:
            if last_gesture != 0 and current_time - last_background_switch > 1000:
                current_background_index = (current_background_index + 1) % len(BACKGROUNDS)
                last_background_switch = current_time
                log(f"切换背景: {BACKGROUNDS[current_background_index]['name']}")
            last_gesture = 0
        
        elif 1 <= gesture <= 4:
            if last_gesture != gesture and current_time - last_creature_summon > 1000:
                creature_manager.summon_creature(gesture)
                last_creature_summon = current_time
            last_gesture = gesture
        
        if hand_data["hand_detected"]:
            creature_manager.update_creature(
                hand_data["hand_x"],
                hand_data["hand_y"],
                hand_data["hand_speed"],
                False
            )
        
        frame = cv2.resize(frame, (RENDER_WIDTH, RENDER_HEIGHT))
        
        bg_id = BACKGROUNDS[current_background_index]["id"]
        bg_path = os.path.join(BACKGROUND_DIR, f"{bg_id}.png")
        if os.path.exists(bg_path):
            bg_img = cv2.imread(bg_path)
            if bg_img is not None:
                bg_img = cv2.resize(bg_img, (RENDER_WIDTH, RENDER_HEIGHT))
                bg_img = cv2.addWeighted(frame, 0.3, bg_img, 0.7, 0)
                frame = bg_img
        
        frame = creature_manager.draw_creature(frame)
        
        creature_info = creature_manager.get_creature_info()
        if creature_info and creature_manager.active_creature:
            creature_x, creature_y = creature_manager.active_creature.get_position()
            frame = draw_creature_info(frame, creature_info, creature_x, creature_y)
        
        fps_count += 1
        elapsed = time.time() - fps_timer
        if elapsed >= 1.0:
            current_fps = fps_count / elapsed
            fps_count = 0
            fps_timer = time.time()
        
        cv2.putText(frame, f'FPS: {current_fps:.0f}', (RENDER_WIDTH - 80, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        bg_name = BACKGROUNDS[current_background_index]["name"]
        frame = cv2_put_text(frame, f'背景: {bg_name} | 手势: {last_gesture}', (20, 30), font_size=20, color=(255, 255, 255))
        
        creature_info = creature_manager.get_creature_info()
        creature_name = creature_info["name"] if creature_info else "无"
        frame = cv2_put_text(frame, f'神兽: {creature_name}', (20, 60), font_size=20, color=(255, 255, 255))
        
        cv2.imshow('山海灵识', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    log("程序结束")
    log_file.close()

if __name__ == "__main__":
    main()