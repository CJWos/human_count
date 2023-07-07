import cv2
import socket
import threading

# 소켓 설정
HOST = "192.168.0.15"
PORT = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')
s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(1)
print('Socket now listening')

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

# 비디오 표시 스레드 함수
def display_video():
    while True:
        # 비디오 프레임 읽기
        ret, frame = cap.read()

        if not ret:
            break

        # 물체 감지 수행
        # ...

        # 결과 영상 출력
        cv2.imshow('Object Detection', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 비디오 캡처 해제
    cap.release()
    cv2.destroyAllWindows()

# 소켓 통신 스레드 함수
def socket_communication():
    while True:
        # 소켓 통신을 위한 접속 승인
        print("Waiting for connection...")
        conn, addr = s.accept()
        print("Connected by", addr)

        # 데이터 수신
        data = conn.recv(1024)
        data = data.decode("utf8").strip()
        if not data:
            break
        print("Received:", data)

        # 수신한 데이터로 파이를 컨트롤
        if data == 'close':
            break
        res = "Status: " + status
        print("파이 동작:", res)

        # 개수에 따른 상태를 클라이언트에 전송
        conn.sendall(res.encode("utf-8"))

        conn.close()

    # 연결 닫기
    s.close()

# 비디오 표시 스레드 시작
video_thread = threading.Thread(target=display_video)
video_thread.start()

# 소켓 통신 스레드 시작
socket_thread = threading.Thread(target=socket_communication)
socket_thread.start()

# 메인 스레드가 종료되기 전에 스레드들이 완료될 때까지 대기
video_thread.join()
socket_thread.join()
