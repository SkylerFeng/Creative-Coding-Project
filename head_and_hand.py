import cv2
import mediapipe as mp
import math

class HandAndHeadControl:
    def __init__(self):
        # 初始化手部识别
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

        # 初始化面部识别
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.8, min_tracking_confidence=0.8)

        # 画图工具
        self.mp_draw = mp.solutions.drawing_utils

    def get_hands(self, frame):
        """
        获取左右手的中心坐标，并返回一个包含左右手信息的对象
        :param frame: 捕获的图像帧
        :return: hands 对象，包含 left 和 right
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        hands = {'left': None, 'right': None}  # 初始化一个字典来存储左右手的中心坐标

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_type = results.multi_handedness[idx].classification[0].label  # 获取是左手还是右手

                # 计算手的中心坐标
                x_sum = 0
                y_sum = 0
                for landmark in hand_landmarks.landmark:
                    x_sum += landmark.x
                    y_sum += landmark.y
                center = (int((x_sum / len(hand_landmarks.landmark)) * frame.shape[1]),
                          int((y_sum / len(hand_landmarks.landmark)) * frame.shape[0]))

                # 根据手的类型存储中心坐标
                if hand_type == 'Left':
                    hands['left'] = center
                elif hand_type == 'Right':
                    hands['right'] = center

                # 绘制手部关键点
                for landmark in hand_landmarks.landmark:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # 绿色圆点标记关键点
                # 绘制手部连接线
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return hands

    def get_head_center(self, frame):
        """
        获取头部的中心坐标
        :param frame: 捕获的图像帧
        :return: 头部的中心坐标 (x, y)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        head_center = None

        if results.multi_face_landmarks:
            for face_landmark in results.multi_face_landmarks:
                # 计算面部关键点的平均坐标作为头部中心
                x_sum = 0
                y_sum = 0
                for landmark in face_landmark.landmark:
                    x_sum += landmark.x
                    y_sum += landmark.y
                head_center = (int((x_sum / len(face_landmark.landmark)) * frame.shape[1]),
                               int((y_sum / len(face_landmark.landmark)) * frame.shape[0]))
                # 在图像上绘制面部关键点
                for landmark in face_landmark.landmark:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)  # 红色圆点标记面部关键点

        return head_center
