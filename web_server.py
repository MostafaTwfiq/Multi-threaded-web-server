import threading
import socket
MY_HOST = "127.0.0.1"
MY_PORT = 65432
BUFFER_SIZE = 1024
def server():
    try:
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((MY_HOST, MY_PORT))
                s.listen()
                conn, addr = s.accept()
                conn_thread = threading.Thread(target=thread_fn, args=(conn, addr))
                conn_thread.start()
    except KeyboardInterrupt:
        print(1)


        
def thread_fn(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            ## Receive HTTP MSG. 
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            result = parse_http_request(data=data)
            conn.sendall(data)

# Parse GET and POST
def parse_http_request(data):
    pass

def write_http_respond(status):
    pass

# Store File on POST Request
def store_file(file_name, file_data):
    with open(file_name, mode='w') as file: 
        file.write(file_data)

# Get file in GET Request
def read_file(file_name):
    file_content = None
    with open(file_name, mode='rb') as file: 
        fileContent = file.read()
    return file_content

if __name__ == "__main__":
    server()