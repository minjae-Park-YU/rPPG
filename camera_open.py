import cv2
camera_index = 0

cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print("Can't open Camera")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Can't read frame")
        break
    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
