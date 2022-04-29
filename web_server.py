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
            conn, addr = s.accept()
            conn_thread = threading.Thread(target=thread_fn, args=(conn, addr))
            conn_thread.start()


        
def thread_fn(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            ## Receive HTTP MSG. 
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            result = parse_data(data=data)
            conn.sendall(data)

def parse_data(data):
    pass

def store_file(file_name, file_data):
    pass

def read_file(file_name):
    pass

if __name__ == "__main__":
    server()