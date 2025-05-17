import cv2
from head_and_hand import HandAndHeadControl  # 导入 HandAndHeadControl 类

# 初始化 HandAndHeadControl 类
hand_and_head_control = HandAndHeadControl()

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 获取手部数据和头部中心坐标
    hands = hand_and_head_control.get_hands(frame)
    head_center = hand_and_head_control.get_head_center(frame)

    # 打印每次获取到的坐标
    print("Left Hand Center:", hands['left'])
    print("Right Hand Center:", hands['right'])
    print("Head Center:", head_center)

    # 在摄像头帧中标记并显示左手、右手和头部中心坐标
    if hands['left']:
        cv2.circle(frame, hands['left'], 5, (0, 255, 0), -1)  # 绿色标记左手
        cv2.putText(frame, f"Left Hand Center: {hands['left']}", (hands['left'][0] + 10, hands['left'][1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        

    if hands['right']:
        cv2.circle(frame, hands['right'], 5, (255, 0, 0), -1)  # 蓝色标记右手
        cv2.putText(frame, f"Right Hand Center: {hands['right']}", (hands['right'][0] + 10, hands['right'][1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    if head_center:
        cv2.circle(frame, head_center, 5, (0, 0, 255), -1)  # 红色标记头部
        cv2.putText(frame, f"Head Center: {head_center}", (head_center[0] + 10, head_center[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 显示摄像头图像
    cv2.imshow("Hand and Head Detection", frame)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
