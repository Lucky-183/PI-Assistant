import socket
import pyaudio
import wave
from threading import Thread
import requests
import time
from config import config
from const_config import UdpbroadcastAdd
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 16000  # Record at 44100 samples per second
filename = "Sound/question.wav"
stream=None
p=None
frames=[]
lock=False
startlock=False
server_socket=None
ready=0
session=requests.session()
def start():
    global stream,p,frames,lock,startlock
    try:
        p = pyaudio.PyAudio()  # Create an interface to PortAudio
        print('Recording')
        config.set(rec_enable=True)
        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)
    except:
        print('start recoding fail')
        startlock=False
        return
    frames = []  # Initialize array to store frames
    # Store data in chunks for 3 seconds
    while(not lock):
        try:
            data = stream.read(chunk)
            # print(data)
            frames.append(data)
        except:
            print('exit')
            startlock=False
            return
    startlock=False
    config.set(rec_enable=False)

def stop():
# Stop and close the stream
    global stream,p,frames,lock,startlock

    while (startlock):
        time.sleep(0.2)
    # lock=True
    if stream is None or p is None or frames is None or lock is False:
        lock=False
        return
    try:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print('Finished recording')

        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        session.get('http://127.0.0.1:5000/command?words=get_audio_complete')
    except:
        print('wrong in record stop ')
        lock=False
        return
    lock=False
    print('stop record complete')

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def udp_hi():
    global server_socket
    if server_socket:
        server_socket.sendto('hi'.encode(), (UdpbroadcastAdd,1234))

def udp_server():
    host='0.0.0.0'
    port=6666
    global lock,server_socket,startlock
    # 创建UDP套接字
    lastda = ''
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind((host, port))
    print(f"UDP服务器正在监听 {host}:{port}")

    while True:
        try:
            # 接收数据和客户端地址
            data, client_address = server_socket.recvfrom(1024)
            if not data:
                continue
            da=data.decode()
            print(f"接收到来自 {client_address} 的数据: {data.decode()}")
            response = "ok".encode()
            if lock is False :
                if da=='start listen':
                    if da != lastda and (startlock is False):
                        s=Thread(target=start)
                        startlock=True
                        s.start()
                    response='START_LISTEN'.encode()
                elif da=='stop listen':
                    if da != lastda :
                        lock=True
                        s2=Thread(target=stop)
                        s2.start()
                    response='STOP_LISTEN'.encode()
                lastda = da
            elif lock is True and da == 'stop listen':
                response = 'STOP_LISTEN'.encode()
            elif da=='button push':
                response='BUTTON_PUSH'.encode()
            elif da=='BUTTON_RELEASE':
                response='button release'.encode()

            # response = "服务器已收到消息".encode()
            server_socket.sendto(response, client_address)

        except KeyboardInterrupt:
            # 捕获Ctrl+C按键，优雅地关闭服务器
            print("UDP服务器已关闭")
            break

if __name__ == "__main__":
    udp_server()
