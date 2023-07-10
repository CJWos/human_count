import cv2
import socket
import multiprocessing as mp
import RPi.GPIO as GPIO

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)  # GPIO 18을 출력으로 설정합니다.

# LED 제어 함수
def do_some_stuffs_with_input(input_string):
    if input_string == "TURN_ON":
        GPIO.output(18, GPIO.HIGH)  # LED를 켭니다.
        return "LED를 켰습니다."
    elif input_string == "TURN_OFF":
        GPIO.output(18, GPIO.LOW)  # LED를 끕니다.
        return "LED를 껐습니다."
    else:
        return "잘못된 명령어입니다."

# LED 제어 소켓 통신 함수
def led_control():
    HOST_LED = "10.137.209.131"
    PORT_LED = 8084
        s_led = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('LED Socket created')
    s_led.bind((HOST_LED, PORT_LED))
    print('LED Socket bind complete')
    s_led.listen(1)
    print('LED Socket now listening')

    while True:
        conn_led, addr_led = s_led.accept()
        print("Connected by", addr_led)

        data_led = conn_led.recv(1024)
        if not data_led:
            break

        data_led = data_led.decode("utf8").strip()
        print("Received (LED):", data_led)

        res_led = do_some_stuffs_with_input(data_led)
        print("파이 동작 (LED):", res_led)

        conn_led.sendall(res_led.encode("utf-8"))
        conn_led.close()

    s_led.close()

# 물체 감지 소켓 통신 함수
def object_detection():
    HOST_DETECT = "10.137.209.131"
    PORT_DETECT = 8083

    s_detect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Detection Socket created')
    s_detect.bind((HOST_DETECT, PORT_DETECT))
    print('Detection Socket bind complete')
    s_detect.listen(1)
    print('Detection Socket now listening')

    # 물체 감지를 위한 설정
    prototxt = '/home/mdp1/Desktop/human_count-main/pot/MobileNetSSD_deploy.prototxt'
    model = '/home/mdp1/Desktop/human_count-main/pot/MobileNetSSD_deploy.caffemodel'
    min_confidence = 0.5

    # 클래스 레이블
    class_labels = [
        'background', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
        'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
        'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
        'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
        'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
        'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
        'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass',
        'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
        'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
        'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
        'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush'
    ]

    # 원하는 물체의 클래스 레이블
    target_label = 'bird'

    # 모델 로드
    net = cv2.dnn.readNetFromCaffe(prototxt, model)

    # 비디오 캡처 객체 생성
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        net.setInput(blob)
        detections = net.forward()

        object_count = 0

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > min_confidence:
                class_id = int(detections[0, 0, i, 1])
                class_label = class_labels[class_id]

                if class_label == target_label:
                    x_left_bottom = int(detections[0, 0, i, 3] * width)
                    y_left_bottom = int(detections[0, 0, i, 4] * height)
                    x_right_top = int(detections[0, 0, i, 5] * width)
                    y_right_top = int(detections[0, 0, i, 6] * height)

                    cv2.rectangle(frame, (x_left_bottom, y_left_bottom), (x_right_top, y_right_top), (0, 255, 0), 2)
                    label = f"{class_label}: {confidence:.2f}"
                    cv2.putText(frame, label, (x_left_bottom, y_left_bottom - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)

                    object_count += 1

        print("Detected objects:", object_count)

        if 0 <= object_count <= 2:
            status = "쾌적"
        elif 3 <= object_count <= 5:
            status = "평범"
        elif 6 <= object_count <= 8:
            status = "포화"
        else:
            status = "알 수 없음"

        print("Status:", status)

        cv2.imshow('Object Detection', frame)

        conn_detect, addr_detect = s_detect.accept()
        print("Connected by", addr_detect)

        data_detect = status.encode("utf-8")
        conn_detect.sendall(data_detect)

        conn_detect.close()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    s_detect.close()
    cap.release()
    cv2.destroyAllWindows()

# 메인 함수
def main():
    # 프로세스 생성 및 시작
    p_led = mp.Process(target=led_control)
    p_detect = mp.Process(target=object_detection)

    p_led.start()
    p_detect.start()

    # 프로세스 종료 대기
    p_led.join()
    p_detect.join()

# 메인 함수 실행
if __name__ == '__main__':
    main()


