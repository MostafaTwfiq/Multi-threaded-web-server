import threading
import socket
import email
import os
from os import path

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
            conn_thread = threading.Thread(target=conn_thread_fn, args=(conn, addr))
            conn_thread.start()


def conn_thread_fn(conn, addr):
    requests_queue = []
    conn_flag = [True]
    requests_thread = threading.Thread(target=conn_thread_fn, args=(conn, requests_queue, conn_flag))
    requests_thread.start()
    with conn:
        print(f"Connected by {addr}")
        message = b''
        while True:
            try:
                # Receive HTTP MSG.
                conn.settimeout(10)
                data = conn.recv(BUFFER_SIZE)
                conn.settimeout(None)
                message += data
                message, request_dict = parse_http_request(data=message)
                if request_dict is not None:
                    if request_dict['http_version'] == b'HTTP/1.0':
                        server_result = get_response(request_dict)
                        http_response = write_http_respond(request_dict, server_result)
                        conn.sendall(http_response)
                        # TODO: check if the server will close the connection or the client
                        break
                    elif request_dict['http_version'] == b'HTTP/1.1':
                        requests_queue.append(request_dict)

            except:
                print('Time Out')
                break

        conn_flag[0] = False


def requests_thread_fn(conn, requests_queue, conn_flag):
    while conn_flag[0]:
        if len(requests_queue) > 0:
            request_dict = requests_queue.pop()
            server_result = get_response(request_dict)
            http_response = write_http_respond(request_dict, server_result)
            conn.sendall(http_response)


def parse_http_request(data):  # data must be bytes
    if b'\r\n\r\n' not in data:
        return data, None

    request, remaining_data = data.split(b'\r\n\r\n', 1)
    start_line, headers = request.split(b'\r\n', 1)
    message = email.message_from_bytes(headers)
    request_dict = dict(message.items())
    # parsing first line
    splitted_start_line = start_line.split(b' ')
    request_dict['method'] = splitted_start_line[0]
    request_dict['file_name'] = splitted_start_line[1]
    request_dict['http_version'] = splitted_start_line[2]
    if request_dict['method'] == b'POST' and int(request_dict['Content-Length'].decode()) <= len(remaining_data):
        request_dict['file_data'], remaining_data = remaining_data.split('\r\n', 1)

    return remaining_data, request_dict


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
        file = server_result['body']
        return STATUS_200 + b'Content-Length: ' + str(
            len(file)).encode() + sperator + b'Connection: keep-alive' + sperator + sperator + file + sperator
    # For POST Request
    elif server_result['status'] == 200 and message_dic['method'] == b'POST':
        return STATUS_200 + b'Content-Length: 0' + sperator + b'Connection: keep-alive' + sperator + sperator
    elif server_result['status'] == 404:
        return STATUS_404 + b'Content-Length: 0' + sperator + b'Connection: keep-alive' + sperator + sperator


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
