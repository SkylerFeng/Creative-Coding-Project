import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()
    if ret:
        print(f"✅ 摄像头 {i} 可用")
        cv2.imshow(f"Camera {i}", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    cap.release()
