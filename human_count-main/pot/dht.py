import socket
import time
import Adafruit_DHT

sensor = Adafruit_DHT.DHT11
pin = 4

# 소켓 서버 정보
HOST = '127.0.0.1'  # 서버 IP 주소
PORT = 1234  # 서버 포트 번호

def send_data_to_server(data):
    try:
        # 소켓 생성
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 서버에 연결
            s.connect((HOST, PORT))
            
            # 데이터 전송
            s.sendall(data.encode())

    except socket.error as e:
        print(f"Socket error: {e}")

try:
    while True:
        h, t = Adafruit_DHT.read_retry(sensor, pin)

        if h is not None and t is not None:
            data = "Temperature = {0:0.1f}*C Humidity = {1:0.1f}%".format(t, h)
            print(data)
            
            # 데이터를 서버로 전송
            send_data_to_server(data)

        else:
            print('Read error')
            time.sleep(100)

except KeyboardInterrupt:
    print("Terminated by Keyboard")

finally:
    print("End of Program")
