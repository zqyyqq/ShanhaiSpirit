import cv2
import mediapipe as mp
import time

print("[1/5] 导入库完成")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
print("[2/5] MediaPipe初始化完成")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print("[3/5] 摄像头打开:", cap.isOpened())

success, frame = cap.read()
print("[4/5] 读取第一帧:", success, "帧大小:", frame.shape if success else "None")

cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Test', 640, 480)
print("[5/5] 窗口创建完成，开始显示...")

start_time = time.time()
count = 0

while True:
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0]
            for i, lm in enumerate(landmarks.landmark):
                x, y = int(lm.x * 640), int(lm.y * 480)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        count += 1
        fps = count / (time.time() - start_time)
        cv2.putText(frame, f'FPS: {fps:.1f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("测试结束")