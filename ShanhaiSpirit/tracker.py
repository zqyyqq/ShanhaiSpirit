"""
《山海灵识》- SIGGRAPH 实时人机交互艺术作品
追踪模块 - tracker.py

功能说明：
独立封装 MediaPipe 手部+面部追踪类，输出手势编号、手部坐标、嘴部开合状态
支持左右手兼容的手势识别，适合交互式艺术展区展出

技术栈：
- MediaPipe Hands：手部21关键点追踪
- MediaPipe FaceMesh：面部468关键点追踪
- OpenCV：摄像头采集

作者：ShanhaiSpirit Team
日期：2026
"""

import cv2
import mediapipe as mp
import numpy as np

# MediaPipe 模块初始化
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

# 手势编号常量
GESTURE_NONE = 0
GESTURE_SUMMON_ZHUQUE = 1
GESTURE_SUMMON_YINGLONG = 2
GESTURE_SUMMON_QILIN = 3
GESTURE_SUMMON_XUANWU = 4
GESTURE_SWITCH_BACKGROUND = 5

# 手势名称映射
GESTURE_MAP = {
    GESTURE_NONE: "无手势",
    GESTURE_SUMMON_ZHUQUE: "召唤朱雀",
    GESTURE_SUMMON_YINGLONG: "召唤应龙",
    GESTURE_SUMMON_QILIN: "召唤麒麟",
    GESTURE_SUMMON_XUANWU: "召唤玄武",
    GESTURE_SWITCH_BACKGROUND: "切换背景",
}

# 嘴部开合检测阈值
MOUTH_OPEN_THRESHOLD = 0.03
MOUTH_UPPER_LANDMARK = 13
MOUTH_LOWER_LANDMARK = 14

# 检测置信度参数
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5


class HandTracker:
    """
    手部追踪类：处理手部关键点检测和手势识别
    支持左右手兼容，输出手势编号和手部坐标
    """

    def __init__(self):
        # 初始化 MediaPipe Hands
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        
        # 追踪状态变量
        self.hand_detected = False
        self.hand_coordinates = (0.5, 0.5)  # 归一化坐标 (0-1)
        self.current_gesture = GESTURE_NONE
        self.finger_states = [False] * 5
        self.last_hand_coordinates = (0.5, 0.5)
        self.hand_speed = 0.0
        self.is_right_hand = True

    def is_right_handed(self, landmarks):
        """判断左右手：根据手腕和拇指尖端的相对位置"""
        if landmarks is None:
            return True
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        return thumb_tip.x > wrist.x

    def detect_finger_state(self, landmarks, finger_index):
        """
        检测单个手指的伸直/弯曲状态
        finger_index: 0=拇指, 1=食指, 2=中指, 3=无名指, 4=小指
        """
        if finger_index == 0:
            # 拇指检测：比较指尖和手掌根部的距离
            thumb_tip = landmarks[4]
            palm_base = landmarks[0]
            # 计算拇指尖到手掌根部的欧氏距离
            distance = ((thumb_tip.x - palm_base.x) ** 2 + 
                        (thumb_tip.y - palm_base.y) ** 2) ** 0.5
            return distance > 0.15
        else:
            tip = landmarks[finger_index * 4 + 3]
            pip = landmarks[finger_index * 4 + 2]
            mcp = landmarks[finger_index * 4]
            
            if finger_index in [3, 4]:
                return tip.y < pip.y
            else:
                return tip.y < pip.y and tip.y < mcp.y

    def detect_gesture(self, landmarks):
        """
        根据手指状态识别手势
        返回手势编号
        """
        if landmarks is None:
            return GESTURE_NONE

        # 判断左右手
        self.is_right_hand = self.is_right_handed(landmarks)

        # 检测每个手指的状态
        finger_states = []
        for i in range(5):
            finger_states.append(self.detect_finger_state(landmarks, i))

        self.finger_states = finger_states

        # 手势识别逻辑
        if finger_states == [True, True, True, True, True]:
            # 五指完全张开 → 切换背景
            return GESTURE_SWITCH_BACKGROUND
        elif finger_states == [False, True, False, False, False]:
            # 只有食指伸直 → 召唤朱雀 (1指)
            return GESTURE_SUMMON_ZHUQUE
        elif finger_states == [False, True, True, False, False]:
            # 食指+中指伸直 → 召唤应龙 (2指)
            return GESTURE_SUMMON_YINGLONG
        elif finger_states == [False, True, True, True, False]:
            # 食指+中指+无名指伸直 → 召唤麒麟 (3指)
            return GESTURE_SUMMON_QILIN
        elif finger_states == [False, True, True, True, True]:
            # 食指+中指+无名指+小指伸直 → 召唤玄武 (4指)
            return GESTURE_SUMMON_XUANWU
        elif finger_states == [False, False, False, False, False]:
            # 握拳 → 召唤玄武 (备选)
            return GESTURE_SUMMON_XUANWU
        else:
            return GESTURE_NONE

    def process_frame(self, frame):
        """
        处理单帧图像，返回追踪结果字典
        输入: OpenCV BGR 格式图像
        输出: 包含手部检测状态、坐标、手势的字典
        """
        # 转换为 RGB 格式（MediaPipe 需要 RGB）
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            # 检测到手部
            landmarks = results.multi_hand_landmarks[0].landmark
            
            # 使用食指根部关键点作为手部坐标（关键点9）
            x = landmarks[9].x
            y = landmarks[9].y

            # 计算手部移动速度
            self.hand_speed = np.sqrt(
                (x - self.last_hand_coordinates[0]) ** 2 +
                (y - self.last_hand_coordinates[1]) ** 2
            ) * 100

            # 更新坐标记录
            self.last_hand_coordinates = (x, y)
            self.hand_coordinates = (x, y)
            self.hand_detected = True
            self.current_gesture = self.detect_gesture(landmarks)

            return {
                "hand_detected": True,
                "hand_x": x,
                "hand_y": y,
                "hand_speed": self.hand_speed,
                "gesture": self.current_gesture,
                "landmarks": landmarks,
                "finger_states": self.finger_states,
                "is_right_hand": self.is_right_hand,
            }
        else:
            # 未检测到手部
            self.hand_detected = False
            self.current_gesture = GESTURE_NONE
            return {
                "hand_detected": False,
                "hand_x": self.hand_coordinates[0],
                "hand_y": self.hand_coordinates[1],
                "hand_speed": 0.0,
                "gesture": GESTURE_NONE,
                "landmarks": None,
                "finger_states": [False] * 5,
                "is_right_hand": self.is_right_hand,
            }

    def draw_hand(self, frame, landmarks):
        """
        在图像上绘制手部关键点和连接线
        用于调试和可视化
        """
        if landmarks:
            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=1),
            )
        return frame

    def get_tracking_result(self):
        """返回当前追踪状态的快照"""
        return {
            "hand_detected": self.hand_detected,
            "hand_x": self.hand_coordinates[0],
            "hand_y": self.hand_coordinates[1],
            "hand_speed": self.hand_speed,
            "gesture": self.current_gesture,
            "finger_states": self.finger_states,
        }


class FaceTracker:
    """
    面部追踪类：处理面部关键点检测和嘴部开合状态
    使用 MediaPipe FaceMesh 468关键点
    """

    def __init__(self):
        # 初始化 MediaPipe FaceMesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        # 追踪状态变量
        self.face_detected = False
        self.mouth_open = False
        self.mouth_ratio = 0.0

    def process_frame(self, frame):
        """
        处理单帧图像，返回面部追踪结果
        输入: OpenCV BGR 格式图像
        输出: 包含面部检测状态和嘴部开合的字典
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            # 检测到面部
            landmarks = results.multi_face_landmarks[0].landmark
            
            # 获取嘴部关键点
            upper_lip = landmarks[MOUTH_UPPER_LANDMARK]
            lower_lip = landmarks[MOUTH_LOWER_LANDMARK]

            # 计算嘴部开合比例（归一化距离）
            self.mouth_ratio = abs(lower_lip.y - upper_lip.y)
            self.mouth_open = self.mouth_ratio > MOUTH_OPEN_THRESHOLD
            self.face_detected = True

            return {
                "face_detected": True,
                "mouth_open": self.mouth_open,
                "mouth_ratio": self.mouth_ratio,
            }
        else:
            # 未检测到面部
            self.face_detected = False
            self.mouth_open = False
            self.mouth_ratio = 0.0

            return {
                "face_detected": False,
                "mouth_open": False,
                "mouth_ratio": 0.0,
            }

    def get_tracking_result(self):
        """返回当前面部追踪状态的快照"""
        return {
            "face_detected": self.face_detected,
            "mouth_open": self.mouth_open,
            "mouth_ratio": self.mouth_ratio,
        }


class CombinedTracker:
    """
    组合追踪器：整合手部和面部追踪
    提供统一的追踪接口
    """

    def __init__(self):
        self.hand_tracker = HandTracker()
        self.face_tracker = FaceTracker()

    def process_frame(self, frame):
        """
        处理单帧图像，同时进行手部和面部追踪
        返回组合结果字典
        """
        hand_result = self.hand_tracker.process_frame(frame)
        face_result = self.face_tracker.process_frame(frame)

        return {
            "hand": hand_result,
            "face": face_result,
        }

    def draw_landmarks(self, frame):
        """在图像上绘制所有关键点"""
        hand_result = self.hand_tracker.process_frame(frame)
        if hand_result["landmarks"]:
            frame = self.hand_tracker.draw_hand(frame, hand_result["landmarks"])
        return frame

    def get_hand_tracker(self):
        """获取手部追踪器实例"""
        return self.hand_tracker

    def get_face_tracker(self):
        """获取面部追踪器实例"""
        return self.face_tracker


# 测试代码
if __name__ == "__main__":
    print("《山海灵识》追踪模块测试")
    
    # 初始化摄像头
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 初始化追踪器
    tracker = CombinedTracker()
    
    print("测试开始，请把手放入画面")
    print("按 'q' 退出")
    
    while True:
        success, frame = cap.read()
        if not success:
            print("无法读取摄像头")
            break
        
        # 水平翻转（镜像效果）
        frame = cv2.flip(frame, 1)
        
        # 处理追踪
        result = tracker.process_frame(frame)
        
        # 显示手势信息
        if result["hand"]["hand_detected"]:
            gesture_name = GESTURE_MAP.get(result["hand"]["gesture"], "未知")
            cv2.putText(frame, f"手势: {gesture_name}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"坐标: ({result['hand']['hand_x']:.2f}, {result['hand']['hand_y']:.2f})", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "未检测到手", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 显示嘴部状态
        if result["face"]["mouth_open"]:
            cv2.putText(frame, "嘴巴张开", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # 绘制手部关键点
        frame = tracker.draw_landmarks(frame)
        
        # 显示画面
        cv2.imshow("山海灵识 - 追踪测试", frame)
        
        # 退出条件
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    print("测试结束")
