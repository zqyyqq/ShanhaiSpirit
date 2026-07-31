import cv2
from tracker import HandTracker, GESTURE_MAP

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

tracker = HandTracker()

print('手势调试模式 - 按 Q 退出')
print('手指索引: 0=拇指, 1=食指, 2=中指, 3=无名指, 4=小指')

finger_names = ['拇指', '食指', '中指', '无名指', '小指']

while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    result = tracker.process_frame(frame)
    
    if result['hand_detected']:
        gesture_name = GESTURE_MAP.get(result['gesture'], '未知')
        cv2.putText(frame, f'手势: {gesture_name}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        for i, state in enumerate(result['finger_states']):
            color = (0, 255, 0) if state else (0, 0, 255)
            status = '伸' if state else '屈'
            text = f'{finger_names[i]}: {status}'
            cv2.putText(frame, text, (10, 60 + i * 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    cv2.imshow('手势调试', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()