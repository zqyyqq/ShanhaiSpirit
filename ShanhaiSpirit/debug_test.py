import cv2
import mediapipe as mp
import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_file = open(os.path.join(BASE_DIR, 'debug_log.txt'), 'w')

def log(msg):
    log_file.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')
    log_file.flush()
    print(msg)

log("开始调试测试")

try:
    log("导入库完成")
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
    log("MediaPipe初始化完成")
    
    log("尝试打开摄像头...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if cap.isOpened():
        log("摄像头打开成功")
        
        log("尝试读取第一帧...")
        for i in range(10):
            success, frame = cap.read()
            if success and frame is not None:
                log(f"帧读取成功! 形状: {frame.shape}")
                break
            time.sleep(0.1)
        else:
            log("帧读取失败")
            cap.release()
            log_file.close()
            sys.exit(1)
        
        log("创建窗口...")
        cv2.namedWindow('Debug', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Debug', 640, 480)
        log("窗口创建完成")
        
        log("开始循环...")
        start_time = time.time()
        count = 0
        
        while True:
            success, frame = cap.read()
            if success:
                frame = cv2.flip(frame, 1)
                count += 1
                fps = count / (time.time() - start_time)
                
                cv2.putText(frame, f'FPS: {fps:.1f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, 'Press Q to quit', (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                cv2.imshow('Debug', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                log("用户按Q退出")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        log("测试结束")
    
    else:
        log("摄像头打开失败")
        
except Exception as e:
    log(f"错误: {str(e)}")

log_file.close()