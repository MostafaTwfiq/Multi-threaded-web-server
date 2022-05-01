import threading
import socket
from os import path

MY_HOST = "127.0.0.1"
MY_PORT = 65432
BUFFER_SIZE = 2048
STATUS_200 = "HTTP/1.0 200 OK\r\n"
STATUS_404 = "HTTP/1.0 404 Not Found\r\n"

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
            print(data)
            if not data:
                break
            result = parse_http_request(data=data)
            server_result = get_response(result=result)
            http_response = write_http_respond(result, server_result)
            conn.sendall(http_response)

# Parse GET and POST
def parse_http_request(data):
    result = {}
    data_list = data.split('\r\n')
    header = data_list[0].split('/')
    if header[0] == 'POST':
        result['type_req'] = header[0] 
        result['http_version'] = header[1]
        result['connection'] = data_list[2].split(':')[1]
        result['file_name'] = ''
        result['body'] = ''
    else:
        result['type_req'] = header[0]
        result['file_name'] = header[1]
        result['http_version'] = header[2]
        result['connection'] = data_list[2].split(':')[1]

    return result

# Get status of the request
def get_response(result):
    server_result = {}
    if result['type_req'] == "POST":
        check = store_file(result['file_name'], result['file_data'])
        if check:
            server_result['status'] = 200
        else:
            server_result['status'] = 404
    elif result['type_req'] == "GET":
        file_data = read_file(result['file_name'],)
        if file_data:
            server_result['status'] = 200
            server_result['body'] = file_data
        else:
            server_result['status'] = 404

    return server_result


# Write Respond
def write_http_respond(result, server_result):    
    # For GET Requests
    if server_result['status'] == 200 and result['type_req'] == "GET":
        return STATUS_200 + server_result['body'] 
    elif server_result['status'] == 404:
        return STATUS_404
    # For POST Request
    elif server_result['status'] == 200 and result['type_req'] == "POST":
        return STATUS_200

# Store File on POST Request
def store_file(file_name, file_data):
    with open(file_name, mode='w') as file: 
        file.write(file_data)
    return path.exists(file_name)

# Get file in GET Request
def read_file(file_name):
    file_content = None
    with open(file_name, mode='rb') as file: 
        fileContent = file.read()
    return file_content

if __name__ == "__main__":
    server()