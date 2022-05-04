import threading
import socket
import email
import os
from os import path
from io import StringIO

MY_HOST = b'127.0.0.1'
MY_PORT = 80
BUFFER_SIZE = 4096
STATUS_200 = b'HTTP/1.1 200 OK\r\n\r\n'
STATUS_404 = b'HTTP/1.1 404 Not Found\r\n\r\n'
PATH = "server_data"


def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((MY_HOST, MY_PORT))
        while True:
            s.listen()
            conn, addr = s.accept()
            conn_thread = threading.Thread(target=thread_fn, args=(conn, addr))
            conn_thread.start()


def thread_fn(conn, addr):
    with conn:
        conn.settimeout(10)
        print(f"Connected by {addr}")
        message = b''
        while True:
            try:
                ## Receive HTTP MSG. 
                data = conn.recv(BUFFER_SIZE)
                if len(data) == 0:
                    break
                message += data
            except:
                print('Time Out')
                break

        headers_dic = parse_http_request(data=message)
        server_result = get_response(headers_dic)
        http_response = write_http_respond(headers_dic, server_result)
        conn.sendall(http_response)


def parse_http_request(data):  # data must be bytes
    data = data.decode(encoding='UTF-8')
    start_line, headers = data.split('\r\n', 1)
    # construct a message from the request string
    message = email.message_from_file(StringIO(headers.replace('\r\n\r\n', '\r\nfile_data:')))
    # construct a dictionary containing the headers
    headers = dict(message.items())
    # parsing first line
    splitted_start_line = start_line.split(' ')
    headers["method"] = splitted_start_line[0]
    headers["file_name"] = splitted_start_line[1]
    headers["http_version"] = splitted_start_line[2]
    return headers


# Get status of the request
def get_response(message_dic):
    server_result = {}
    if message_dic["method"] == "POST":
        file_exist = store_file(message_dic['file_name'], message_dic['file_data'])
        if file_exist:
            server_result['status'] = 200
        else:
            server_result['status'] = 404
    elif message_dic["method"] == "GET":
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
    if server_result['status'] == 200 and message_dic['method'] == "GET":
        return STATUS_200 + server_result['body'].encode(encoding='UTF-8')
    # For POST Request
    elif server_result['status'] == 200 and message_dic['method'] == "POST":
        return STATUS_200
    elif server_result['status'] == 404:
        return STATUS_404


# Store File on POST Request
def store_file(file_name, file_data):
    file_path = PATH + os.sep + file_name
    file_data = file_data.encode(encoding='UTF-8')
    if not path.exists(file_path):
        return False

    with open(file_path, mode='wb') as file:
        file.write(file_data)

    return True


# Get file in GET Request
def read_file(file_name):
    file_content = None
    file_path = PATH + os.sep + file_name
    try:
        with open(file_path, mode='rb') as file:
            file_content = file.read()
    except:
        return file_content

    return file_content


if __name__ == "__main__":
    server()
