import email
import socket
import os
import sys
from threading import *
import webbrowser

opened_connections = {}  # label: [requests_queue]

HTTP_VERSION = b'HTTP/1.1'
SERVER_IP = b'127.0.0.1'
BUFFER_SIZE = 4096
PATH = "client_data"


def commands_exec_thread(host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        requests_queue = []
        sent_requests_queue = []
        opened_connections[host] = requests_queue
        ip, port = host.split(':')
        s.connect((ip, int(port)))
        rec_resp_thread = Thread(target=receive_responses_thread, args=(s, sent_requests_queue))
        rec_resp_thread.start()

        while True:
            if len(requests_queue) > 0:
                request = requests_queue.pop()
                method, file_name, _ = request.split(b' ', 2)
                try:
                    s.sendall(request)
                except:
                    break
                sent_requests_queue.append([method, file_name])

    del opened_connections[host]


def receive_responses_thread(conn, sent_requests_queue):
    with conn:
        message = b''
        while True:
            data = conn.recv(BUFFER_SIZE)
            if len(data) == 0:
                break
            message += data
            message, response_dict = parse_http_response(message, sent_requests_queue[0][0])
            if response_dict is not None:
                execute_response(response_dict, sent_requests_queue.pop())


def client(command_file):
    commands = read_commands(command_file)
    for command in commands:
        request, ip, port = generate_http_request(command)
        host = ip + port
        if str(host) not in opened_connections:
            comm_exec_thread = Thread(target=commands_exec_thread, args=host)
            comm_exec_thread.start()
            while host not in opened_connections:
                continue

        opened_connections[host].append(request)


def read_commands(command_file):
    commands = None
    with open(command_file, mode='r') as file:
        commands = file.read().split('\n')
    return commands


def execute_response(response_dict, method_and_file):
    if method_and_file[0] == 'GET' and response_dict['response_code'] == b'200':
        store_file(method_and_file[1], response_dict['file_data'])


def parse_http_response(data, method):  # data must be bytes
    if b'\r\n\r\n' not in data:
        return data, None

    response, remaining_data = data.split(b'\r\n\r\n', 1)
    start_line, headers = response.split(b'\r\n', 1)
    message = email.message_from_bytes(headers)
    response_dict = dict(message.items())
    # parsing first line
    splitted_start_line = start_line.split(b' ', 3)
    response_dict['http_version'] = splitted_start_line[0]
    response_dict['response_code'] = splitted_start_line[1]
    response_dict['response_state'] = splitted_start_line[2]
    if method == 'GET' and int(response_dict['Content-Length'].decode()) <= len(remaining_data):
        response_dict['file_data'], remaining_data = remaining_data.split('\r\n', 1)

    return remaining_data, response_dict


def generate_http_request(command):
    command = command.encode(encoding='UTF-8')
    request = b''
    splitted_command = command.split(b' ')
    ip = splitted_command[2]
    port = bytes(80 if len(splitted_command) < 4 else splitted_command[3])
    request = request + splitted_command[0] + b' ' + splitted_command[1] + b' ' + HTTP_VERSION + b'\r\n'
    request = request + b'HOST: ' + ip + b':' + port + b'\r\n' + b'Connection: ' + b'keep-alive' + b'\r\n'

    if splitted_command[0] == b'GET':
        request = request + get_request_headers("GET") + b'\r\n'
    elif splitted_command[0] == b'POST':
        data = read_file(splitted_command[1].decode(encoding='UTF-8'))
        request = request + b'Content-Type: ' + get_content_type(splitted_command[1].decode(encoding='UTF-8')) + b'\r\n'
        request = request + b'Content-Length:  ' + str(len(data)).encode() + b'\r\n'
        request = request + get_request_headers("POST") + b'\r\n'
        request = request + data + b'\r\n'

    return request, ip.decode(), port.decode()


def get_request_headers(method):
    if method == "GET":
        return b''
    elif method == "POST":
        return b''


def get_content_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == '.png':
        return b'image/png'
    elif file_extension == '.html':
        return b'text/html'
    elif file_extension == '.txt':
        return b'text/plain'


def store_file(file_name, file_data):
    file_name = file_name
    file_path = PATH + os.sep + file_name
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode='wb') as file:
        file.write(file_data)
    webbrowser.open(os.path.realpath(file_path))


def read_file(file_name):
    file_content = None
    file_path = PATH + os.sep + file_name
    with open(file_path, mode='rb') as file:
        file_content = file.read()

    return file_content


if __name__ == "__main__":
    client(sys.argv[1])
