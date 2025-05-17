import cv2
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

class HandAndHeadControl:
    def __init__(self):
        # 加载 MoveNet 模型（PoseNet 升级版）
        self.model = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/4")
        self.input_size = 256

        # 关键点索引参考（17个关键点）
        self.WRIST_LEFT = 9
        self.WRIST_RIGHT = 10
        self.NOSE = 0
        self.SHOULDER_LEFT = 5
        self.SHOULDER_RIGHT = 6

    def detect_pose(self, frame):
        # 预处理图像
        img = cv2.resize(frame, (self.input_size, self.input_size))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        input_tensor = tf.convert_to_tensor(img_rgb, dtype=tf.int32)
        input_tensor = tf.expand_dims(input_tensor, axis=0)

        # 推理
        outputs = self.model.signatures['serving_default'](input_tensor)
        keypoints = outputs['output_0'].numpy()[0, 0, :, :]  # (17, 3): y, x, confidence
        return keypoints

    def get_hands(self, frame):
        keypoints = self.detect_pose(frame)
        h, w = frame.shape[:2]
        hands = {'left': None, 'right': None}

        # 左手腕
        y, x, c = keypoints[self.WRIST_LEFT]
        if c > 0.3:
            left = (int(x * w), int(y * h))
            hands['left'] = left
            cv2.circle(frame, left, 6, (0, 255, 0), -1)
            cv2.putText(frame, "LEFT", (left[0] + 10, left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 右手腕
        y, x, c = keypoints[self.WRIST_RIGHT]
        if c > 0.3:
            right = (int(x * w), int(y * h))
            hands['right'] = right
            cv2.circle(frame, right, 6, (255, 0, 0), -1)
            cv2.putText(frame, "RIGHT", (right[0] + 10, right[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        return hands


    def get_head_center(self, frame):
        keypoints = self.detect_pose(frame)
        h, w = frame.shape[:2]

        # 1. 优先用鼻子
        y, x, c = keypoints[self.NOSE]
        if c > 0.3:
            head = (int(x * w), int(y * h))
            cv2.circle(frame, head, 6, (0, 0, 255), -1)
            return head

        # 2. fallback：用肩膀中点
        l_shoulder = keypoints[self.SHOULDER_LEFT]
        r_shoulder = keypoints[self.SHOULDER_RIGHT]
        if l_shoulder[2] > 0.3 and r_shoulder[2] > 0.3:
            cx = int((l_shoulder[1] + r_shoulder[1]) / 2 * w)
            cy = int((l_shoulder[0] + r_shoulder[0]) / 2 * h) - 30  # 向上估计头部
            head = (cx, cy)
            cv2.circle(frame, head, 6, (0, 0, 255), -1)
            return head

        return None
