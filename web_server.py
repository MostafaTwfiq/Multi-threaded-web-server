import threading
import socket
MY_HOST = "127.0.0.1"
MY_PORT = 65432
BUFFER_SIZE = 1024
def server():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((MY_HOST, MY_PORT))
            s.listen()
            conn_thread = threading.Thread(target=thread_fn, args=(s,))
            conn_thread.start()

        
def thread_fn(s):
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                conn.sendall(data)

def parse_data(data):
    pass
