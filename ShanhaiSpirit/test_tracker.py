import cv2
import mediapipe as mp
import numpy as np
import time
import os
from PIL import Image, ImageDraw, ImageFont

def cv2_put_text(img, text, pos, font_size=20, color=(0, 255, 0)):
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

print("初始化 MediaPipe Hands...")
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

print("打开摄像头...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    cap.release()
    cap = cv2.VideoCapture(0)

print("摄像头打开成功！按 Q 退出")

finger_names = ['大拇指', '食指', '中指', '无名指', '小指']
frame_count = 0
start_time = time.time()

while True:
    success, frame = cap.read()
    if not success or frame is None:
        time.sleep(0.01)
        continue
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]
        
        mp_drawing.draw_landmarks(
            frame,
            landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        
        finger_states = []
        for i in range(5):
            if i == 0:
                tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
                mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
                extended = abs(tip.x - mcp.x) > abs(ip.x - mcp.x) * 1.2
            else:
                tip = landmarks.landmark[mp_hands.HandLandmark(i * 4 + 4)]
                pip = landmarks.landmark[mp_hands.HandLandmark(i * 4 + 2)]
                extended = tip.y < pip.y
            finger_states.append(extended)
        
        extended_count = sum(finger_states)
        frame = cv2_put_text(frame, f'手势: {extended_count}', (20, 40), font_size=36, color=(0, 255, 0))
        
        y_offset = 80
        for i, (name, state) in enumerate(zip(finger_names, finger_states)):
            color = (0, 255, 0) if state else (0, 0, 255)
            status = '伸' if state else '弯'
            frame = cv2_put_text(frame, f'{name}: {status}', (20, y_offset + i * 30), font_size=24, color=color)
    
    else:
        frame = cv2_put_text(frame, '未检测到手', (20, 40), font_size=36, color=(0, 0, 255))
    
    frame_count += 1
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0
    cv2.putText(frame, f'FPS: {fps:.1f}', (500, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.imshow('手势追踪测试', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("测试结束")