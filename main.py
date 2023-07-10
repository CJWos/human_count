import socket
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN) # 입력 설정

HOST = "192.168.0.6"
PORT = 9021
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')
s.bind((HOST, PORT))
print ('Socket bind complete')
s.listen(1)
print ('Socket now listening')

#파이 컨트롤 함수
def do_some_stuffs_with_input(input_string):
    #라즈베리파이를 컨트롤할 명령어 설정
   if input_string == "send":      #휴대폰에서 send 라는 값이 올경우 ...라는 값을 돌려준다.
        input_string = "..."
   else :
        input_string = input_string + " 없는 명령어 입니다."
   return input_string
   
while True:
    
     #접속 승인
    print("s")
    conn, addr = s.accept()
    print("Connected by ", addr)

    #데이터 수신
    data = conn.recv(1024)
    print("a")
    data = data.decode("utf8").strip()
    if not data: break
    print("Received: " + data)

    #수신한 데이터로 파이를 컨트롤 
    if data == 'close':
        break;
    res = do_some_stuffs_with_input(data)
    print("파이 동작 :" + res)
    if GPIO.input(17) == 1:  # 16번 GPIO에 입력값이 들어올경우 ...이라는 값 대신에 push값전달
        print("in")
        command =("push")
        conn.sendall(command.encode("utf-8")) 
    else:#클라이언트에게 답을 보냄
        conn.sendall(res.encode("utf-8"))
    conn.close()
    print("c")
    #연결 닫기
s.close()
