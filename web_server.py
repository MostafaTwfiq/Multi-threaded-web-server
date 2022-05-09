import threading
import socket
import email
import os
from os import path
from io import StringIO

MY_HOST = b'127.0.0.1'
MY_PORT = 80
BUFFER_SIZE = 4096
sperator = b'\r\n'
STATUS_200 = b'HTTP/1.1 200 OK' + sperator
STATUS_404 = b'HTTP/1.1 404 Not Found' + sperator
PATH = "server_data"


def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((MY_HOST, MY_PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            conn_thread = threading.Thread(target=thread_fn, args=(conn, addr))
            conn_thread.start()


def thread_fn(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        message = b''
        request_dict = {}
        f = 0
        while True:
            try:
                # Receive HTTP MSG.
                conn.settimeout(10)
                data = conn.recv(BUFFER_SIZE)
                conn.settimeout(None)
                message += data
                if len(message) == 0:
                    f = 1
                    break
                
                request_dict = parse_http_request(data=message)
                if len(request_dict['file_data']) == int(request_dict['Content-Length']):
                    break
                elif len(request_dict['file_data']) > int(request_dict['Content-Length']):
                    f = 1
                    print("Error in body")
                    break
            except:
                print('Time Out')
                break
        if f == 0:
            server_result = get_response(request_dict)
            http_response = write_http_respond(request_dict, server_result)
            conn.sendall(http_response)


def parse_http_request(data):  # data must be bytes
    request_dict = {}
    header, body = data.split(b'\r\n\r\n', 1)
    header_list = header.split(b'\r\n')
    request_dict['method'] = header_list[0].split(b' ')[0]
    request_dict['file_name'] = header_list[0].split(b' ')[1]
    request_dict['http_version'] = header_list[0].split(b' ')[2]
    for h in header_list:
        line = h.split(b' ')
        if b'Connection:' in line:
            request_dict['Connection'] = line[-1]
        elif b'Content-Length:' in line:
            request_dict['Content-Length'] = line[-1]
    if request_dict['method'] == b'POST':
        request_dict['file_data'] = body
    else:
        request_dict['file_data'] = ''
    return request_dict


# Get status of the request
def get_response(message_dic):
    server_result = {}
    if message_dic['method'] == b'POST':
        file_exist = store_file(message_dic['file_name'], message_dic['file_data'])
        if file_exist:
            server_result['status'] = 200
        else:
            server_result['status'] = 404
    elif message_dic['method'] == b'GET':
        file_data = read_file(message_dic['file_name'])
        if file_data:
            server_result['status'] = 200
            server_result['body'] = file_data
        else:
            server_result['status'] = 404

    return server_result


# Write Respond
def write_http_respond(message_dic, server_result):
    # For GET Requests
    if server_result['status'] == 200 and message_dic['method'] == b'GET':
        file =  server_result['body']
        return STATUS_200 + b'Content-Length: '+ str(len(file)).encode() + sperator + b'Connection: keep-alive'+ sperator + sperator + file
    # For POST Request
    elif server_result['status'] == 200 and message_dic['method'] == b'POST':
        return STATUS_200 + b'Content-Length: 0' + sperator + b'Connection: keep-alive' + sperator + sperator + b''
    elif server_result['status'] == 404:
        return STATUS_404 + b'Content-Length: 0' + sperator + b'Connection: keep-alive' + sperator + sperator + b''


# Store File on POST Request
def store_file(file_name, file_data):
    file_name = file_name.decode(encoding='UTF-8')
    file_path = PATH + os.sep + file_name
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, mode='wb') as file:
        file.write(file_data)

    if not path.exists(file_path):
        return False
    return True


# Get file in GET Request
def read_file(file_name):
    file_content = None
    file_name = file_name.decode(encoding='UTF-8')
    file_path = PATH + os.sep + file_name
    try:
        with open(file_path, mode='rb') as file:
            file_content = file.read()
    except:
        return file_content
    return file_content


if __name__ == "__main__":
    server()
