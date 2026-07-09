import cv2
import mediapipe as mp
import time

print("初始化...")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("开始循环...")

while True:
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        gesture = 0
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0]
            
            finger_states = []
            for i in range(5):
                if i == 0:
                    tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
                    mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
                    finger_states.append(abs(tip.x - mcp.x) > abs(ip.x - mcp.x) * 1.2)
                else:
                    tip = landmarks.landmark[mp_hands.HandLandmark(i * 4 + 4)]
                    pip = landmarks.landmark[mp_hands.HandLandmark(i * 4 + 2)]
                    finger_states.append(tip.y < pip.y)
            
            extended_count = sum(finger_states)
            gesture = extended_count if 1 <= extended_count <= 4 else 0
            
            wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]
            print(f"手势: {gesture}, 位置: ({wrist.x:.2f}, {wrist.y:.2f})")
        
        cv2.putText(frame, f'Gesture: {gesture}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("结束")