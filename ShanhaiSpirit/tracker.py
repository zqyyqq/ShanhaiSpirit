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
GESTURE_FIST = 6
GESTURE_HIDE_YUN = 7

# 手势名称映射
GESTURE_MAP = {
    GESTURE_NONE: "无手势",
    GESTURE_SUMMON_ZHUQUE: "召唤朱雀",
    GESTURE_SUMMON_YINGLONG: "召唤青龙",
    GESTURE_SUMMON_QILIN: "召唤白虎",
    GESTURE_SUMMON_XUANWU: "召唤玄武",
    GESTURE_SWITCH_BACKGROUND: "切换背景",
    GESTURE_FIST: "握拳",
    GESTURE_HIDE_YUN: "隐藏云",
}

# 嘴部开合检测阈值
MOUTH_OPEN_THRESHOLD = 0.03
MOUTH_UPPER_LANDMARK = 13
MOUTH_LOWER_LANDMARK = 14

# 检测置信度参数
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# 双手检测稳定性参数
HANDS_STABILITY_FRAMES = 3
FIST_STABILITY_FRAMES = 5


class HandTracker:
    """
    手部追踪类：处理手部关键点检测和手势识别
    支持左右手兼容，输出手势编号和手部坐标
    支持双手检测
    """

    def __init__(self, mirror=True):
        # 初始化 MediaPipe Hands
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        
        # 镜像配置：摄像头画面是否镜像显示
        self.mirror = mirror
        
        # 追踪状态变量
        self.hand_detected = False
        self.hand_coordinates = (0.5, 0.5)
        self.current_gesture = GESTURE_NONE
        self.finger_states = [False] * 5
        self.last_hand_coordinates = (0.5, 0.5)
        self.hand_speed = 0.0
        self.is_right_hand = True
        
        # 双手检测状态
        self.hands_detected = False
        self.hands_count = 0
        self.hands_open = False
        self.hands_fist = False
        self.hands_gestures = []
        
        # 双手检测稳定性历史
        self.hands_count_history = []
        self.hands_fist_history = []
        self.stable_hands_count = 0
        self.stable_hands_fist = False
        
        # 保存MediaPipe results用于绘制
        self.last_results = None
        
        # 手势稳定性过滤
        self.gesture_history = []
        self.gesture_stability_threshold = 5
        
        # 手势冷却时间（毫秒）
        self.last_gesture_switch_time = 0
        self.gesture_switch_cooldown = 150

    def is_right_handed(self, landmarks):
        """判断左右手：根据手腕和拇指尖端的相对位置"""
        if landmarks is None:
            return True
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        
        if self.mirror:
            return thumb_tip.x < wrist.x
        else:
            return thumb_tip.x > wrist.x

    def detect_finger_state(self, landmarks, finger_index):
        """
        检测单个手指的伸直/弯曲状态
        finger_index: 0=拇指, 1=食指, 2=中指, 3=无名指, 4=小指
        """
        if finger_index == 0:
            return self._detect_thumb_state(landmarks)
        else:
            return self._detect_finger_state_normal(landmarks, finger_index)

    def _detect_thumb_state(self, landmarks):
        """
        检测拇指伸直状态
        使用指尖到手腕的距离比值：当拇指伸直时，指尖远离手腕
        """
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        index_mcp = landmarks[5]
        wrist = landmarks[0]
        
        # 指尖到手腕的距离
        tip_to_wrist = np.sqrt((thumb_tip.x - wrist.x) ** 2 + (thumb_tip.y - wrist.y) ** 2)
        
        # MCP到手腕的距离（拇指根部到手腕）
        mcp_to_wrist = np.sqrt((thumb_mcp.x - wrist.x) ** 2 + (thumb_mcp.y - wrist.y) ** 2)
        
        # 避免除零错误
        if mcp_to_wrist < 0.001:
            return False
        
        # 距离比值：拇指伸直时，tip_to_wrist 明显大于 mcp_to_wrist
        ratio = tip_to_wrist / mcp_to_wrist
        
        # 当比值大于1.6时认为拇指伸直
        is_extended = ratio > 1.6
        
        return is_extended

    def _detect_finger_state_normal(self, landmarks, finger_index):
        """
        检测食指、中指、无名指、小指的伸直状态
        使用指尖与MCP的距离判断：指尖距离MCP较远即为伸直
        """
        tip = landmarks[finger_index * 4 + 3]
        pip = landmarks[finger_index * 4 + 2]
        mcp = landmarks[finger_index * 4 + 1]
        wrist = landmarks[0]
        
        # 计算指尖到MCP的距离
        tip_to_mcp = np.sqrt((tip.x - mcp.x) ** 2 + (tip.y - mcp.y) ** 2)
        
        # 计算PIP到MCP的距离（作为参考）
        pip_to_mcp = np.sqrt((pip.x - mcp.x) ** 2 + (pip.y - mcp.y) ** 2)
        
        # 指尖到MCP的距离大于PIP到MCP的距离则认为伸直
        # 并且指尖在MCP上方（y更小）
        is_extended = tip_to_mcp > pip_to_mcp * 1.1 and tip.y < mcp.y
        
        return is_extended

    def detect_gesture(self, landmarks):
        """
        根据手指状态识别手势
        返回手势编号
        """
        if landmarks is None:
            return GESTURE_NONE

        self.is_right_hand = self.is_right_handed(landmarks)

        finger_states = []
        for i in range(5):
            finger_states.append(self.detect_finger_state(landmarks, i))

        self.finger_states = finger_states

        if finger_states == [True, True, True, True, True]:
            raw_gesture = GESTURE_SWITCH_BACKGROUND
        elif finger_states == [False, True, False, False, False]:
            raw_gesture = GESTURE_SUMMON_ZHUQUE
        elif finger_states == [False, True, True, False, False]:
            raw_gesture = GESTURE_SUMMON_YINGLONG
        elif finger_states == [False, True, True, True, False]:
            raw_gesture = GESTURE_SUMMON_QILIN
        elif finger_states == [False, True, True, True, True]:
            raw_gesture = GESTURE_SUMMON_XUANWU
        elif finger_states == [False, False, False, False, False]:
            raw_gesture = GESTURE_FIST
        elif finger_states == [True, False, False, False, False]:
            raw_gesture = GESTURE_HIDE_YUN
        else:
            raw_gesture = GESTURE_NONE
        
        # 保存原始手势用于显示
        self.raw_gesture = raw_gesture
        
        self.gesture_history.append(raw_gesture)
        if len(self.gesture_history) > self.gesture_stability_threshold:
            self.gesture_history.pop(0)
        
        gesture_counts = {}
        for g in self.gesture_history:
            gesture_counts[g] = gesture_counts.get(g, 0) + 1
        
        if gesture_counts:
            candidate_gesture = max(gesture_counts, key=gesture_counts.get)
            max_count = gesture_counts[candidate_gesture]
            
            if max_count >= self.gesture_stability_threshold - 1:
                current_time = cv2.getTickCount() / cv2.getTickFrequency() * 1000
                if current_time - self.last_gesture_switch_time >= self.gesture_switch_cooldown:
                    self.last_gesture_switch_time = current_time
                    return candidate_gesture
            
            return self.current_gesture
        
        return GESTURE_NONE

    def detect_hand_open(self, landmarks):
        """检测一只手是否张开（五指伸直）"""
        if landmarks is None:
            return False
        finger_states = []
        for i in range(5):
            finger_states.append(self.detect_finger_state(landmarks, i))
        return all(finger_states)
    
    def detect_fist(self, landmarks):
        """检测一只手是否握拳（五指弯曲）"""
        if landmarks is None:
            return False
        finger_states = []
        for i in range(5):
            finger_states.append(self.detect_finger_state(landmarks, i))
        return not any(finger_states)
    
    def get_hand_coords(self, landmarks):
        """从关键点获取归一化坐标"""
        raw_x = landmarks[9].x
        raw_y = landmarks[9].y
        wrist_raw_x = landmarks[0].x
        wrist_raw_y = landmarks[0].y
        
        if self.mirror:
            x = 1.0 - raw_x
            y = raw_y
        else:
            x = raw_x
            y = raw_y
        
        return x, y, wrist_raw_x, wrist_raw_y
    
    def update_stability(self, hands_count, is_fist):
        """更新双手检测稳定性历史"""
        self.hands_count_history.append(hands_count)
        self.hands_fist_history.append(is_fist)
        
        # 保持历史长度
        if len(self.hands_count_history) > HANDS_STABILITY_FRAMES * 2:
            self.hands_count_history.pop(0)
        if len(self.hands_fist_history) > FIST_STABILITY_FRAMES * 2:
            self.hands_fist_history.pop(0)
        
        # 计算稳定的手数：取众数
        if len(self.hands_count_history) >= HANDS_STABILITY_FRAMES:
            counts = {}
            for c in self.hands_count_history:
                counts[c] = counts.get(c, 0) + 1
            self.stable_hands_count = max(counts, key=counts.get)
        
        # 计算稳定的握拳状态：最近N帧都是握拳才认为稳定
        if len(self.hands_fist_history) >= FIST_STABILITY_FRAMES:
            recent = self.hands_fist_history[-FIST_STABILITY_FRAMES:]
            self.stable_hands_fist = all(recent)
    
    def process_frame(self, frame):
        """
        处理单帧图像，返回追踪结果字典
        输入: OpenCV BGR 格式图像
        输出: 包含手部检测状态、坐标、手势、双手状态的字典
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        self.last_results = results

        raw_hands_count = 0
        raw_hands_fist = False
        self.hands_gestures = []
        right_hand_x = 0.5
        right_hand_y = 0.5
        self.hand_detected = False
        self.current_gesture = GESTURE_NONE
        
        if results.multi_hand_landmarks:
            raw_hands_count = len(results.multi_hand_landmarks)
            self.hands_gestures = []
            
            # 判断右手（在镜像模式下，右手的x坐标较小）
            right_hand_idx = 0
            if raw_hands_count >= 2:
                hand0_wrist_x = results.multi_hand_landmarks[0].landmark[0].x
                hand1_wrist_x = results.multi_hand_landmarks[1].landmark[0].x
                if self.mirror:
                    # 镜像模式：右手在屏幕左侧，x较小
                    right_hand_idx = 0 if hand0_wrist_x < hand1_wrist_x else 1
                else:
                    # 非镜像模式：右手在屏幕右侧，x较大
                    right_hand_idx = 0 if hand0_wrist_x > hand1_wrist_x else 1
            
            # 获取右手坐标
            right_hand_landmarks = results.multi_hand_landmarks[right_hand_idx].landmark
            right_hand_x, right_hand_y, _, _ = self.get_hand_coords(right_hand_landmarks)
            
            for hand_landmarks in results.multi_hand_landmarks:
                hand_gesture = self.detect_gesture(hand_landmarks.landmark)
                self.hands_gestures.append(hand_gesture)
            
            # 检查双手握拳状态（原始检测）
            if raw_hands_count >= 2:
                hand1_fist = self.detect_fist(results.multi_hand_landmarks[0].landmark)
                hand2_fist = self.detect_fist(results.multi_hand_landmarks[1].landmark)
                raw_hands_fist = hand1_fist and hand2_fist
            
            # 使用右手进行手势识别和位置控制
            landmarks = right_hand_landmarks
            
            x, y, wrist_x, wrist_y = self.get_hand_coords(landmarks)

            self.hand_speed = np.sqrt(
                (x - self.last_hand_coordinates[0]) ** 2 +
                (y - self.last_hand_coordinates[1]) ** 2
            ) * 100

            self.last_hand_coordinates = (x, y)
            self.hand_coordinates = (x, y)
            self.hand_detected = True
            self.current_gesture = self.detect_gesture(landmarks)
        
        # 更新稳定性
        self.update_stability(raw_hands_count, raw_hands_fist)
        
        # 使用稳定的双手检测结果
        self.hands_count = self.stable_hands_count
        self.hands_fist = self.stable_hands_fist
        self.hands_detected = (self.stable_hands_count >= 2)
        
        if self.hand_detected:
            return {
                "hand_detected": True,
                "hand_x": self.hand_coordinates[0],
                "hand_y": self.hand_coordinates[1],
                "wrist_x": wrist_x if results.multi_hand_landmarks else self.hand_coordinates[0],
                "wrist_y": wrist_y if results.multi_hand_landmarks else self.hand_coordinates[1],
                "hand_speed": self.hand_speed,
                "gesture": self.current_gesture,
                "raw_gesture": self.raw_gesture,  # 原始手势用于显示
                "landmarks": landmarks if results.multi_hand_landmarks else None,
                "finger_states": self.finger_states,
                "is_right_hand": self.is_right_hand,
                "hands_count": self.hands_count,
                "hands_open": self.hands_open,
                "hands_fist": self.hands_fist,
                "hands_gestures": self.hands_gestures.copy(),
                "right_hand_x": right_hand_x,
                "right_hand_y": right_hand_y,
            }
        else:
            self.current_gesture = GESTURE_NONE
            self.raw_gesture = GESTURE_NONE
            self.hands_open = False
            self.hands_fist = False
            self.hands_gestures = []
            return {
                "hand_detected": False,
                "hand_x": self.hand_coordinates[0],
                "hand_y": self.hand_coordinates[1],
                "hand_speed": 0.0,
                "gesture": GESTURE_NONE,
                "raw_gesture": GESTURE_NONE,
                "landmarks": None,
                "finger_states": [False] * 5,
                "is_right_hand": self.is_right_hand,
                "hands_count": 0,
                "hands_open": False,
                "hands_fist": False,
                "hands_gestures": [],
                "right_hand_x": 0.5,
                "right_hand_y": 0.5,
            }

    def draw_hand(self, frame, landmarks, color=(0, 255, 0)):
        """
        在图像上绘制手部关键点和连接线
        用于调试和可视化
        """
        if landmarks:
            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=1),
            )
        return frame
    
    def draw_all_hands(self, frame, results):
        """绘制所有检测到的手部"""
        if results and results.multi_hand_landmarks:
            colors = [(0, 255, 0), (0, 0, 255)]
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                color = colors[i % len(colors)]
                self.draw_hand(frame, hand_landmarks.landmark, color)
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
