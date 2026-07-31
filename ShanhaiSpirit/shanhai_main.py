"""
《山海灵识》- SIGGRAPH 实时人机交互艺术作品
主程序 - OpenCV显示 + pygame粒子系统
"""

import os
import random
import cv2
import numpy as np
import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.mixer.init()

from tracker import (
    HandTracker,
    FaceTracker,
    GESTURE_NONE,
    GESTURE_SUMMON_ZHUQUE,
    GESTURE_SUMMON_YINGLONG,
    GESTURE_SUMMON_QILIN,
    GESTURE_SUMMON_XUANWU,
    GESTURE_SWITCH_BACKGROUND,
    GESTURE_MAP,
    GESTURE_FIST,
    GESTURE_HIDE_YUN,
)

from particle import ParticleManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKGROUND_DIR = os.path.join(ASSETS_DIR, "backgrounds")
CREATURES_DIR = os.path.join(ASSETS_DIR, "creatures")
YUN_DIR = os.path.join(ASSETS_DIR, "yun")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")
KAISHI_DIR = os.path.join(ASSETS_DIR, "kaishi")  # 开始界面资源目录

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
        "name": "青龙",
        "id": "qinglong",
        "description": "《山海经·大荒东经》云："
                       "青龙为东方神兽，"
                       "身如游龙，鳞甲森严，"
                       "掌司春雷，万物复苏。",
    },
    GESTURE_SUMMON_QILIN: {
        "name": "白虎",
        "id": "baihu",
        "description": "《山海经·西山经》云："
                       "白虎为西方神兽，"
                       "体若猛虎，白毛森森，"
                       "掌司秋令，肃杀万物。",
    },
    GESTURE_SUMMON_XUANWU: {
        "name": "玄武",
        "id": "xuanwu",
        "description": "《山海经·北山经》云："
                       "玄武为北方神兽，"
                       "龟蛇相缠，玄冥幽远，"
                       "掌司冬雪，潜藏万物。",
    },
}

def make_seamless(img):
    """将图片制成可无缝平铺的长图（水平镜像拼接）"""
    h, w = img.shape[:2]
    flipped = cv2.flip(img, 1)
    seamless = np.zeros((h, w * 2, 3), dtype=np.uint8)
    seamless[:, :w] = img
    seamless[:, w:] = flipped
    return seamless

def load_backgrounds():
    backgrounds = []
    import glob
    png_pattern = os.path.join(BACKGROUND_DIR, "*.png")
    webp_pattern = os.path.join(BACKGROUND_DIR, "*.webp")
    bg_files = sorted(glob.glob(png_pattern) + glob.glob(webp_pattern))
    
    for bg_path in bg_files:
        img = cv2.imread(bg_path, cv2.IMREAD_UNCHANGED)
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        
        h, w = img.shape[:2]
        
        if h >= WINDOW_HEIGHT:
            crop_start = (h - WINDOW_HEIGHT) // 2
            img = img[crop_start:crop_start + WINDOW_HEIGHT, :]
        else:
            pad_top = (WINDOW_HEIGHT - h) // 2
            pad_bottom = WINDOW_HEIGHT - h - pad_top
            img = cv2.copyMakeBorder(img, pad_top, pad_bottom, 0, 0, cv2.BORDER_REFLECT)
        
        seamless_img = make_seamless(img)
        sh, sw = seamless_img.shape[:2]
        tile_count = max(2, (WINDOW_WIDTH * 2) // sw + 2)
        
        double_width = sw * tile_count
        double_img = np.zeros((sh, double_width, 3), dtype=np.uint8)
        for i in range(tile_count):
            double_img[:, i * sw:(i + 1) * sw] = seamless_img
        
        backgrounds.append({
            'image': double_img,
            'tile_width': sw,
            'total_width': double_width
        })
    
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
                img = remove_white_background(img)
                frames.append(img)
            creatures[data["id"]] = frames
    return creatures


def load_sounds():
    sounds = {}
    import glob
    if os.path.exists(SOUND_DIR):
        wav_files = glob.glob(os.path.join(SOUND_DIR, "*.wav"))
        mp3_files = glob.glob(os.path.join(SOUND_DIR, "*.mp3"))
        
        for f in wav_files:
            name = os.path.splitext(os.path.basename(f))[0]
            sounds[name] = {"type": "wav", "file": f}
        
        for f in mp3_files:
            name = os.path.splitext(os.path.basename(f))[0]
            sounds[name] = {"type": "mp3", "file": f}
    
    return sounds


def play_sound(sounds, name):
    if name in sounds:
        try:
            sound_info = sounds[name]
            if sound_info["type"] == "wav":
                sound = pygame.mixer.Sound(sound_info["file"])
                sound.play()
            elif sound_info["type"] == "mp3":
                pygame.mixer.music.load(sound_info["file"])
                pygame.mixer.music.play()
        except Exception as e:
            print(f"播放声音失败: {e}")


def load_fire_sound():
    """加载喷火音效文件"""
    fire_sound_path = os.path.join(SOUND_DIR, "penhuo.mp3")
    if os.path.exists(fire_sound_path):
        try:
            sound = pygame.mixer.Sound(fire_sound_path)
            sound.set_volume(0.5)  # 设置音量
            return sound
        except Exception as e:
            print(f"加载喷火音效失败: {e}")
            return None
    else:
        print(f"喷火音效文件不存在: {fire_sound_path}")
        return None


def load_water_sound():
    """加载喷水音效文件"""
    water_sound_path = os.path.join(SOUND_DIR, "penshui.wav")
    if os.path.exists(water_sound_path):
        try:
            sound = pygame.mixer.Sound(water_sound_path)
            sound.set_volume(0.5)  # 设置音量
            return sound
        except Exception as e:
            print(f"加载喷水音效失败: {e}")
            return None
    else:
        print(f"喷水音效文件不存在: {water_sound_path}")
        return None


def remove_white_border_rgba(img):
    result = img.copy()
    
    alpha = result[:, :, 3].astype(np.float32) / 255.0
    rgb = result[:, :, :3].astype(np.float32)
    
    opaque_mask = alpha >= 0.95
    if opaque_mask.sum() > 0:
        opaque_rgb = rgb[opaque_mask]
        non_white_opaque = opaque_rgb[np.mean(opaque_rgb, axis=1) < 220]
        if len(non_white_opaque) > 0:
            subject_color = non_white_opaque.mean(axis=0)
        else:
            subject_color = opaque_rgb.mean(axis=0)
    else:
        subject_color = np.array([128, 128, 128])
    
    white_mask = np.mean(rgb, axis=2) > 200
    semi_mask = (alpha > 0.01) & (alpha < 0.95)
    white_semi = white_mask & semi_mask
    
    if white_semi.sum() > 0:
        whiteness = np.clip((np.mean(rgb, axis=2) - 180) / 75, 0, 1)
        strength = whiteness * (1 - alpha) * 2.0
        strength = np.clip(strength, 0, 1)
        
        for c in range(3):
            channel = rgb[:, :, c]
            corrected = np.where(
                white_semi,
                channel + (subject_color[c] - channel) * strength,
                channel
            )
            result[:, :, c] = np.clip(corrected, 0, 255).astype(np.uint8)
        
        # 降低白边区域的透明度（更透明）
        alpha_correction = np.where(
            white_semi,
            alpha * (1 - strength * 0.7),
            alpha
        )
        result[:, :, 3] = (alpha_correction * 255).astype(np.uint8)
    
    return result

def remove_white_background(img):
    if img.shape[2] == 4:
        return remove_white_border_rgba(img)
    h, w = img.shape[:2]
    
    corner_size = max(5, min(h, w) // 10)
    corners = [
        img[:corner_size, :corner_size],
        img[:corner_size, -corner_size:],
        img[-corner_size:, :corner_size],
        img[-corner_size:, -corner_size:],
    ]
    
    bg_colors = []
    for corner in corners:
        bg_colors.append(corner.reshape(-1, 3).mean(axis=0))
    bg_color = np.mean(bg_colors, axis=0)
    
    diff = np.sqrt(np.sum((img.astype(np.float32) - bg_color.astype(np.float32)) ** 2, axis=2))
    
    soft_threshold = 20
    hard_threshold = 50
    
    alpha = np.zeros((h, w), dtype=np.float32)
    alpha[diff >= hard_threshold] = 255.0
    soft_region = (diff > soft_threshold) & (diff < hard_threshold)
    alpha[soft_region] = ((diff[soft_region] - soft_threshold) / (hard_threshold - soft_threshold)) * 255.0
    
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
    
    result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = alpha.astype(np.uint8)
    
    alpha_mask = result[:, :, 3] > 0
    for c in range(3):
        result[:, :, c] = np.where(alpha_mask, result[:, :, c], 0).astype(np.uint8)
    
    return result

def remove_watermark(img):
    """去除图片右下角的水印文字"""
    h, w = img.shape[:2]
    
    # 转灰度检测水印
    if img.shape[2] == 4:
        gray = cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2GRAY)
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 检测右下角区域的暗色文字
    dark_mask = gray < 200
    contours, _ = cv2.findContours(dark_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        # 只处理右下角的小区域（水印特征）
        if area > 300 and x > w * 0.5 and y > h * 0.5 and cw < w * 0.3 and ch < h * 0.3:
            pad = 5
            x1, y1 = max(0, x - pad), max(0, y - pad)
            x2, y2 = min(w, x + cw + pad), min(h, y + ch + pad)
            
            # 采样周围背景色
            sample_region = img[max(0,y1-15):max(0,y1-5), x1:x2]
            if sample_region.size > 0:
                if img.shape[2] == 4:
                    bg = sample_region[:,:,:3].mean(axis=(0,1)).astype(np.uint8)
                    # 4通道图：填充RGB+保留原alpha
                    img[y1:y2, x1:x2, 0] = bg[0]
                    img[y1:y2, x1:x2, 1] = bg[1]
                    img[y1:y2, x1:x2, 2] = bg[2]
                else:
                    bg = sample_region.mean(axis=(0,1)).astype(np.uint8)
                    img[y1:y2, x1:x2] = bg
    
    return img

def overlay_image(frame, img, x, y, size):
    img = cv2.resize(img, (size, size), interpolation=cv2.INTER_LANCZOS4)
    
    if img.shape[2] == 4:
        img_float = img.astype(np.float32) / 255.0
        
        y1 = max(0, y - size // 2)
        y2 = min(frame.shape[0], y + size // 2)
        x1 = max(0, x - size // 2)
        x2 = min(frame.shape[1], x + size // 2)
        
        img_y1 = max(0, size // 2 - y)
        img_y2 = img_y1 + (y2 - y1)
        img_x1 = max(0, size // 2 - x)
        img_x2 = img_x1 + (x2 - x1)
        
        img_region = img_float[img_y1:img_y2, img_x1:img_x2]
        alpha = img_region[:, :, 3:4]
        rgb = img_region[:, :, :3]
        
        frame_region = frame[y1:y2, x1:x2].astype(np.float32) / 255.0
        
        blended = frame_region * (1 - alpha) + rgb * alpha
        
        frame[y1:y2, x1:x2] = (blended * 255).astype(np.uint8)
    else:
        y1 = y - size // 2
        y2 = y + size // 2
        x1 = x - size // 2
        x2 = x + size // 2
        
        if y1 >= 0 and y2 < frame.shape[0] and x1 >= 0 and x2 < frame.shape[1]:
            frame[y1:y2, x1:x2] = img
    
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


def draw_text_box(frame, name, description):
    box_w = 320
    box_h = 160
    margin = 20
    
    # 固定在左下角
    x1 = margin
    y1 = frame.shape[0] - box_h - margin
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x1 + box_w, y1 + box_h), (250, 250, 250), -1)
    cv2.addWeighted(overlay, 0.92, frame, 0.08, 0, frame)
    
    cv2.rectangle(frame, (x1, y1), (x1 + box_w, y1 + box_h), (20, 20, 20), 2)
    
    m = 6
    cv2.rectangle(frame, (x1 + m, y1 + m), (x1 + box_w - m, y1 + box_h - m), (60, 60, 60), 1)
    
    corner_len = 8
    corners = [
        (x1, y1, 1, 1), (x1 + box_w, y1, -1, 1),
        (x1, y1 + box_h, 1, -1), (x1 + box_w, y1 + box_h, -1, -1)
    ]
    for cx, cy, dx, dy in corners:
        cv2.line(frame, (cx, cy), (cx + dx * corner_len, cy), (20, 20, 20), 2)
        cv2.line(frame, (cx, cy), (cx, cy + dy * corner_len), (20, 20, 20), 2)
    
    title_y = y1 + 15
    font_title = get_font(28)
    name_w = font_title.getlength(name)
    name_x = x1 + (box_w - name_w) // 2
    frame = draw_chinese_text(frame, name, name_x, title_y, font_size=28, color=(20, 20, 20))
    
    line_y = title_y + 42
    font = get_font(14)
    description_lines = []
    current_line = ""
    max_chars_per_line = 20
    for char in description:
        if len(current_line) >= max_chars_per_line:
            description_lines.append(current_line)
            current_line = ""
        current_line += char
    if current_line:
        description_lines.append(current_line)
    
    max_lines = 5
    display_lines = description_lines[:max_lines]
    for line in display_lines:
        line_w = font.getlength(line)
        line_x = x1 + (box_w - line_w) // 2
        frame = draw_chinese_text(frame, line, line_x, line_y, font_size=14, color=(40, 40, 40))
        line_y += 20
    
    return frame


def draw_camera_preview(frame, camera_frame):
    """在右上角绘制摄像头预览画面"""
    preview_w = 200
    preview_h = 150
    margin = 20
    
    # 镜像摄像头画面
    camera_frame = cv2.flip(camera_frame, 1)
    
    # 缩放到预览大小
    preview = cv2.resize(camera_frame, (preview_w, preview_h))
    
    # 右上角位置
    x1 = frame.shape[1] - preview_w - margin
    y1 = margin
    
    # 绘制边框
    cv2.rectangle(frame, (x1 - 3, y1 - 3), (x1 + preview_w + 3, y1 + preview_h + 3), (200, 200, 200), 2)
    cv2.rectangle(frame, (x1 - 5, y1 - 5), (x1 + preview_w + 5, y1 + preview_h + 5), (100, 100, 100), 1)
    
    # 叠加预览画面（带透明度，基本看不清脸）
    alpha = 0.25  # 透明度系数（0.0-1.0，越小越透明）
    roi = frame[y1:y1+preview_h, x1:x1+preview_w]
    cv2.addWeighted(preview, alpha, roi, 1.0 - alpha, 0, roi)
    
    # 标签
    label = "摄像头"
    font = get_font(14)
    label_w = font.getlength(label)
    label_x = x1 + (preview_w - label_w) // 2
    frame = draw_chinese_text(frame, label, label_x, y1 + preview_h + 8, font_size=12, color=(255, 255, 255))
    
    return frame


def draw_gesture_panel(frame, result, active_creature=None):
    """绘制左上角手势识别面板"""
    panel_w = 280
    panel_h = 120
    x1 = 15
    y1 = 15
    
    # 面板背景
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x1 + panel_w, y1 + panel_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    cv2.rectangle(frame, (x1, y1), (x1 + panel_w, y1 + panel_h), (255, 255, 255), 1)
    
    y_offset = y1 + 12
    
    if result["hand_detected"]:
        # 使用原始手势（不受稳定性过滤延迟影响）
        display_gesture = result.get("raw_gesture", result["gesture"])
        
        # 根据当前神兽和手势显示对应的功能名称
        gesture_name = GESTURE_MAP.get(display_gesture, "未知")
        # 拇指手势时根据神兽状态显示不同功能
        if display_gesture == GESTURE_HIDE_YUN:
            if active_creature == "zhuque":
                gesture_name = "喷火"
            elif active_creature == "xuanwu":
                gesture_name = "喷水"
            elif active_creature == "qinglong":
                gesture_name = "打雷"
            else:
                gesture_name = "切换祥云"
        
        font_title = get_font(18)
        frame = draw_chinese_text(frame, f"手势: {gesture_name}", x1 + 10, y_offset, font_size=18, color=(255, 220, 100))
        y_offset += 28
        
        finger_names = ['拇', '食', '中', '无', '小']
        finger_status = ""
        for i, state in enumerate(result["finger_states"]):
            finger_status += finger_names[i] + ("●" if state else "○") + " "
        font = get_font(14)
        frame = draw_chinese_text(frame, f"手指: {finger_status}", x1 + 10, y_offset, font_size=14, color=(200, 230, 255))
        y_offset += 24
        
        # 双手状态
        hands_count = result.get("hands_count", 0)
        hands_info = f"双手: {hands_count}只"
        if hands_count >= 2:
            hands_info += f" | 握拳: {'是' if result.get('hands_fist', False) else '否'}"
        frame = draw_chinese_text(frame, hands_info, x1 + 10, y_offset, font_size=14, color=(200, 255, 200))
    else:
        frame = draw_chinese_text(frame, "手势: 未检测到手", x1 + 10, y_offset, font_size=16, color=(180, 180, 180))
    
    return frame


def pygame_to_cv2(surface):
    """将pygame surface转换为OpenCV图像（支持alpha通道）"""
    # 获取RGBA数组
    img = pygame.surfarray.array3d(surface)
    img = np.transpose(img, (1, 0, 2))  # 转置为(height, width, 3)
    
    # 如果surface有alpha通道，获取alpha
    if surface.get_flags() & pygame.SRCALPHA:
        alpha = pygame.surfarray.array_alpha(surface)
        alpha = np.transpose(alpha, (1, 0))  # 转置为(height, width)
        # 扩展alpha到3通道
        alpha_3d = np.stack([alpha] * 3, axis=2)
        # 使用alpha混合
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img, alpha_3d
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img, None


def cv2_to_pygame_surface(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return pygame.surfarray.make_surface(img_rgb)


def show_start_screen():
    """
    显示开始界面：
    1. 显示山海经背景图3秒
    2. 切换到白背景，4神兽图围绕中心点旋转一圈
    3. 旋转完成后返回，进入主界面
    """
    # 创建窗口
    cv2.namedWindow("山海灵识", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("山海灵识", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # ===== 第一阶段：显示山海经背景图3秒 =====
    shanhaijing_path = os.path.join(KAISHI_DIR, "shanhaijing.png")
    shanhaijing_img = None
    if os.path.exists(shanhaijing_path):
        shanhaijing_img = cv2.imread(shanhaijing_path)
        if shanhaijing_img is not None:
            # 缩放到窗口大小
            shanhaijing_img = cv2.resize(shanhaijing_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
    
    if shanhaijing_img is not None:
        start_time = cv2.getTickCount() / cv2.getTickFrequency()
        while True:
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            elapsed = current_time - start_time
            
            if elapsed >= 3.0:
                break
            
            # 显示背景图
            cv2.imshow("山海灵识", shanhaijing_img)
            
            # 检测按键，允许跳过
            key = cv2.waitKey(30) & 0xFF
            if key == 27 or key == ord('q'):  # ESC或Q退出
                cv2.destroyAllWindows()
                return False
    
    return True


def main():
    print("《山海灵识》启动")
    
    # 显示开始界面（山海经背景3秒 + 4神兽旋转一圈）
    if not show_start_screen():
        print("用户退出开始界面")
        return
    
    backgrounds = load_backgrounds()
    creatures = load_creatures()
    sounds = load_sounds()
    
    # 加载并播放背景音乐（用Sound对象，不占用music通道）
    bgm_path = os.path.join(SOUND_DIR, "bj.mp3")
    if os.path.exists(bgm_path):
        try:
            bgm_sound = pygame.mixer.Sound(bgm_path)
            bgm_sound.set_volume(0.5)
            bgm_sound.play(-1)
            print("背景音乐已启动")
        except Exception as e:
            print(f"加载背景音乐失败: {e}")
    
    print(f"加载背景: {len(backgrounds)} 个")
    print(f"加载神兽: {len(creatures)} 个")
    print(f"加载音效: {len(sounds)} 个")
    
    cloud_images = []
    for i in range(1, 10):
        yun_path = os.path.join(YUN_DIR, f"yun{i}.png")
        if os.path.exists(yun_path):
            img = cv2.imread(yun_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                # 去除水印
                img = remove_watermark(img)
                if img.shape[2] == 4:
                    # 4通道图片：硬化alpha，去掉半透明灰边
                    b, g, r, a = cv2.split(img)
                    a = np.where(a >= 128, 255, 0).astype(np.uint8)
                    # 闭运算清理边缘
                    kernel = np.ones((3, 3), np.uint8)
                    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, kernel)
                    img_rgba = cv2.merge((r, g, b, a))
                else:
                    # 3通道图片：只保留深色轮廓，去掉浅色填充
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # 只保留亮度<=225的轮廓部分
                    alpha = np.where(gray <= 225, 255, 0).astype(np.uint8)
                    # 闭运算（膨胀后腐蚀）：填充轮廓内部空隙，不向外扩张
                    kernel = np.ones((3, 3), np.uint8)
                    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
                    
                    b, g, r = cv2.split(img)
                    a = alpha
                    img_rgba = cv2.merge((r, g, b, a))
                
                cloud_img = pygame.image.frombuffer(img_rgba.tobytes(), 
                                                    img_rgba.shape[1::-1], "RGBA")
                cloud_images.append(cloud_img)
    
    yun_path = os.path.join(YUN_DIR, "yun.png")
    if os.path.exists(yun_path):
        img = cv2.imread(yun_path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            if img.shape[2] == 4:
                b, g, r, a = cv2.split(img)
                img_rgba = cv2.merge((r, g, b, a))
            else:
                img = remove_white_background(img)
                b, g, r, a = cv2.split(img)
                img_rgba = cv2.merge((r, g, b, a))
            cloud_img = pygame.image.frombuffer(img_rgba.tobytes(), 
                                                img_rgba.shape[1::-1], "RGBA")
            cloud_images.append(cloud_img)
    
    print(f"加载云图: {len(cloud_images)} 张")
    
    particle_manager = ParticleManager(WINDOW_WIDTH, WINDOW_HEIGHT, cloud_images)
    
    # 创建pygame surface用于粒子渲染
    particle_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    tracker = HandTracker()
    face_tracker = FaceTracker()
    
    current_background = 0
    active_creature = None
    creature_info = None
    show_description = False
    last_mouth_open = False
    last_mouth_sound_time = 0
    
    # 初始化喷火音效
    fire_sound = load_fire_sound()
    fire_sound_channel = pygame.mixer.Channel(1)  # 使用第二个通道
    is_fire_sound_playing = False
    has_fire_sound = fire_sound is not None
    
    # 初始化喷水音效
    water_sound = load_water_sound()
    water_sound_channel = pygame.mixer.Channel(2)  # 使用第三个通道
    is_water_sound_playing = False
    has_water_sound = water_sound is not None
    
    # 初始化青龙打雷音效
    thunder_sound = None
    has_thunder_sound = False
    for ext in [".mp3", ".wav"]:
        thunder_sound_path = os.path.join(SOUND_DIR, f"dalei{ext}")
        if os.path.exists(thunder_sound_path):
            try:
                thunder_sound = pygame.mixer.Sound(thunder_sound_path)
                thunder_sound.set_volume(0.7)
                has_thunder_sound = True
                print(f"加载打雷音效: {thunder_sound_path}")
                break
            except Exception as e:
                print(f"加载打雷音效失败: {e}")
    thunder_sound_channel = pygame.mixer.Channel(3)
    is_thunder_sound_playing = False
    
    creature_x = WINDOW_WIDTH // 2
    creature_y = WINDOW_HEIGHT // 2
    target_x = WINDOW_WIDTH // 2
    target_y = WINDOW_HEIGHT // 2
    
    last_gesture_time = 0
    gesture_cooldown = 1500
    last_thunder_time = 0
    
    bg_offset = 0
    bg_scroll_speed = -0.5
    
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(60) / 1000.0
        
        success, frame = cap.read()
        if not success:
            continue
        
        result = tracker.process_frame(frame)
        face_result = face_tracker.process_frame(frame)
        
        if result["hand_detected"]:
            target_x = int(result["hand_x"] * WINDOW_WIDTH)
            target_y = int(result["hand_y"] * WINDOW_HEIGHT)
            
            gesture = result["gesture"]
            finger_states = result.get("finger_states", [False] * 5)
            
            # 双手都伸食指和中指时，生成随机祥云
            if result.get("hands_count", 0) >= 2 and gesture == GESTURE_SUMMON_YINGLONG:
                current_time = cv2.getTickCount() / cv2.getTickFrequency() * 1000
                if current_time - last_gesture_time > gesture_cooldown:
                    last_gesture_time = current_time
                    particle_manager.spawn_random_cloud(target_x, target_y)
                    print(f"生成随机祥云 (共{len(particle_manager.cloud_particles)}朵)")
                # 跳过青龙召唤
                gesture = GESTURE_NONE
            
            # 朱雀激活时，只伸拇指时喷火
            if active_creature == "zhuque":
                # 只有拇指伸出且其他手指都弯曲时才喷火
                only_thumb = finger_states[0] and not finger_states[1] and not finger_states[2] and not finger_states[3] and not finger_states[4]
                if only_thumb:
                    if not particle_manager.fire_enabled:
                        # 开启喷火
                        particle_manager.set_fire_enabled(True)
                        particle_manager.set_fire_direction("right")
                        # 播放喷火音效
                        if has_fire_sound and not is_fire_sound_playing:
                            fire_sound_channel.play(fire_sound, loops=-1)  # 循环播放
                            is_fire_sound_playing = True
                else:
                    if particle_manager.fire_enabled:
                        # 关闭喷火
                        particle_manager.set_fire_enabled(False)
                        # 停止喷火音效
                        if is_fire_sound_playing:
                            fire_sound_channel.stop()
                            is_fire_sound_playing = False
            
            # 玄武激活时，持续检测拇指状态控制喷水
            if active_creature == "xuanwu":
                # 拇指伸直时喷水，拇指弯曲时停止
                if finger_states[0]:
                    if not particle_manager.water_enabled:
                        # 开启喷水
                        particle_manager.set_water_enabled(True)
                        particle_manager.set_water_direction("right")
                        # 播放喷水音效
                        if has_water_sound and not is_water_sound_playing:
                            water_sound_channel.play(water_sound, loops=-1)  # 循环播放
                            is_water_sound_playing = True
                else:
                    if particle_manager.water_enabled:
                        # 关闭喷水
                        particle_manager.set_water_enabled(False)
                        # 停止喷水音效
                        if is_water_sound_playing:
                            water_sound_channel.stop()
                            is_water_sound_playing = False
            
            # 青龙激活时，大拇指伸出打雷
            if active_creature == "qinglong":
                if finger_states[0]:
                    # 只有拇指伸出时打雷
                    # 雷打在屏幕顶部随机位置（模拟天上打雷），不打在龙身上
                    thunder_x = random.randint(WINDOW_WIDTH // 4, WINDOW_WIDTH * 3 // 4)
                    thunder_y = random.randint(50, WINDOW_HEIGHT // 3)
                    if not particle_manager.thunder_enabled:
                        particle_manager.set_thunder_enabled(True)
                        # 首次触发立即播放音效和粒子
                        if has_thunder_sound and not is_thunder_sound_playing:
                            thunder_sound_channel.play(thunder_sound)
                            is_thunder_sound_playing = True
                        particle_manager.spawn_thunder(thunder_x, thunder_y)
                    else:
                        # 持续触发：每隔一段时间重复打雷
                        current_time = cv2.getTickCount() / cv2.getTickFrequency()
                        if current_time - last_thunder_time > 1.5:  # 1.5秒冷却
                            last_thunder_time = current_time
                            # 每次打雷位置随机
                            thunder_x = random.randint(WINDOW_WIDTH // 4, WINDOW_WIDTH * 3 // 4)
                            thunder_y = random.randint(50, WINDOW_HEIGHT // 3)
                            if has_thunder_sound:
                                thunder_sound_channel.play(thunder_sound)
                            particle_manager.spawn_thunder(thunder_x, thunder_y)
                else:
                    if particle_manager.thunder_enabled:
                        particle_manager.set_thunder_enabled(False)
                        thunder_sound_channel.stop()
                        is_thunder_sound_playing = False
            
            if gesture != GESTURE_NONE:
                current_time = cv2.getTickCount() / cv2.getTickFrequency() * 1000
                if current_time - last_gesture_time > gesture_cooldown:
                    last_gesture_time = current_time
                    
                    if gesture == GESTURE_SWITCH_BACKGROUND:
                        current_background = (current_background + 1) % len(backgrounds)
                        bg_names = []
                        import glob
                        png_pattern = os.path.join(BACKGROUND_DIR, "*.png")
                        webp_pattern = os.path.join(BACKGROUND_DIR, "*.webp")
                        bg_files = sorted(glob.glob(png_pattern) + glob.glob(webp_pattern))
                        for f in bg_files:
                            bg_names.append(os.path.splitext(os.path.basename(f))[0])
                        print(f"切换背景: {bg_names[current_background]}")
                    elif gesture in CREATURES_DATA:
                        creature_info = CREATURES_DATA[gesture]
                        active_creature = creature_info["id"]
                        show_description = False
                        print(f"召唤神兽: {creature_info['name']}")
                        
                        particle_manager.spawn_burst(target_x, target_y, count=60)
                        
                        # 召唤神兽时默认关闭喷火/喷水/打雷和停止音效
                        particle_manager.set_fire_enabled(False)
                        particle_manager.set_water_enabled(False)
                        particle_manager.set_thunder_enabled(False)
                        if is_fire_sound_playing:
                            fire_sound_channel.stop()
                            is_fire_sound_playing = False
                        if is_water_sound_playing:
                            water_sound_channel.stop()
                            is_water_sound_playing = False
                        thunder_sound_channel.stop()
                        is_thunder_sound_playing = False
                    elif gesture == GESTURE_HIDE_YUN:
                        # 非朱雀/玄武时，拇指手势控制祥云显示/隐藏
                        if active_creature not in ["zhuque", "xuanwu"]:
                            particle_manager.toggle_cloud()
                            print(f"祥云: {'开启' if particle_manager.cloud_enabled else '关闭'}")
        
        # 双手握拳时显示简介
        if result.get("hands_fist", False):
            show_description = True
        elif not result.get("hands_detected", False):
            show_description = False
        
        # 张嘴时播放神兽叫声
        mouth_open = face_result.get("mouth_open", False)
        if mouth_open and not last_mouth_open and active_creature:
            current_time = cv2.getTickCount() / cv2.getTickFrequency() * 1000
            if current_time - last_mouth_sound_time > 1000:
                last_mouth_sound_time = current_time
                play_sound(sounds, active_creature)
        last_mouth_open = mouth_open
        
        creature_x += (target_x - creature_x) * 0.15
        creature_y += (target_y - creature_y) * 0.15
        
        bg_offset += bg_scroll_speed * dt * 60
        
        if backgrounds:
            bg_data = backgrounds[current_background]
            total_width = bg_data['total_width']
            if bg_offset >= total_width - WINDOW_WIDTH:
                bg_offset = 0
            elif bg_offset < 0:
                bg_offset = total_width - WINDOW_WIDTH - 1
            
            bg_img = bg_data['image']
            display_frame = bg_img[:, int(bg_offset):int(bg_offset) + WINDOW_WIDTH].copy()
        else:
            bg_offset = 0
            display_frame = np.full((WINDOW_HEIGHT, WINDOW_WIDTH, 3), 200, dtype=np.uint8)
        
        beast_pos = (int(creature_x), int(creature_y)) if active_creature else None
        particle_manager.update(dt, beast_pos, active_creature)
        
        # 先绘制神兽后面的祥云（yun7）到particle_surface
        particle_surface.fill((0, 0, 0, 0))
        particle_manager.draw_cloud_behind(particle_surface)
        particle_img, particle_alpha = pygame_to_cv2(particle_surface)
        if particle_alpha is not None:
            alpha_norm = (particle_alpha[:, :, 0:1].astype(np.float32) / 255.0)
            alpha_3ch = np.repeat(alpha_norm, 3, axis=2)
            display_frame = (
                display_frame.astype(np.float32) * (1 - alpha_3ch) +
                particle_img.astype(np.float32) * alpha_3ch
            ).astype(np.uint8)
        
        # 绘制神兽
        if active_creature and creature_info:
            frames = creatures.get(active_creature, [])
            if frames:
                img = frames[0]
                creature_size = int(WINDOW_WIDTH * 0.3)
                display_frame = overlay_image(display_frame, img, int(creature_x), int(creature_y), creature_size)
            
            if show_description:
                display_frame = draw_text_box(display_frame, creature_info["name"], creature_info["description"])
        
        # 再绘制神兽前面的祥云（yun1-6）+ 火焰 + 喷水 + 打雷
        particle_surface.fill((0, 0, 0, 0))
        particle_manager.draw_cloud_front(particle_surface)
        # 绘制火焰、喷水和打雷粒子（在最上层）
        for p in particle_manager.fire_particles:
            p.draw(particle_surface)
        for p in particle_manager.water_particles:
            p.draw(particle_surface)
        for p in particle_manager.thunder_particles:
            p.draw(particle_surface)
        
        particle_img, particle_alpha = pygame_to_cv2(particle_surface)
        if particle_alpha is not None:
            alpha_norm = (particle_alpha[:, :, 0:1].astype(np.float32) / 255.0)
            alpha_3ch = np.repeat(alpha_norm, 3, axis=2)
            display_frame = (
                display_frame.astype(np.float32) * (1 - alpha_3ch) +
                particle_img.astype(np.float32) * alpha_3ch
            ).astype(np.uint8)
        
        # 绘制屏幕闪光效果（模拟闪电照亮）
        if particle_manager.screen_flash:
            flash_alpha = int((particle_manager.screen_flash.life / particle_manager.screen_flash.max_life) * 220)
            if flash_alpha > 0:
                flash_overlay = np.full((WINDOW_HEIGHT, WINDOW_WIDTH, 3), 235, dtype=np.uint8)
                cv2.addWeighted(flash_overlay, flash_alpha / 255.0, display_frame, 1.0, 0, display_frame)
        
        # 右上角摄像头预览
        display_frame = draw_camera_preview(display_frame, frame)
        
        # 左上角手势识别面板
        display_frame = draw_gesture_panel(display_frame, result, active_creature)
        
        # 底部操作提示
        display_frame = draw_chinese_text(display_frame, "双手握拳显示简介 | 张嘴发声 | Q退出",
                                          WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 20, font_size=14, color=(255, 255, 255))
        
        cv2.imshow("山海灵识", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('f') or key == ord('F'):
            is_fullscreen = cv2.getWindowProperty("山海灵识", cv2.WND_PROP_FULLSCREEN)
            if is_fullscreen:
                cv2.setWindowProperty("山海灵识", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            else:
                cv2.setWindowProperty("山海灵识", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    print("《山海灵识》关闭")


if __name__ == "__main__":
    main()