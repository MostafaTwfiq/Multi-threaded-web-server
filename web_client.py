import email
import socket
import os
import sys
import threading
import webbrowser

HTTP_VERSION = b'HTTP/1.1'
SERVER_IP = b'127.0.0.1'
HTTP_PORT = 80
BUFFER_SIZE = 4096
PATH = "client_data"


def commands_exec_thread(conn, commands, requests_methods):
    for command in commands:
        request = generate_http_request(command)
        method, file_name, _ = request.split(b' ', 2)
        conn.sendall(request)
        requests_methods.append([method, file_name])


def receive_responses_thread(conn, requests_methods):
    with conn:
        message = b''
        while True:
            data = conn.recv(BUFFER_SIZE)
            if len(data) == 0:
                break
            message += data
            message, response_dict = parse_http_response(message, requests_methods[0][0])
            if response_dict is not None:
                execute_response(response_dict, requests_methods.pop())


def client(command_file):
    commands = read_commands(command_file)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, HTTP_PORT))
        requests_methods = []
        comm_exec_thread = threading.Thread(target=commands_exec_thread, args=(s, commands, requests_methods))
        rec_resp_thread = threading.Thread(target=receive_responses_thread, args=(s, commands, requests_methods))
        comm_exec_thread.start()
        rec_resp_thread.start()


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
    request = request + splitted_command[0] + b' ' + splitted_command[1] + b' ' + HTTP_VERSION + b'\r\n'
    request = request + b'HOST: ' + splitted_command[2] + b':' + bytes(
        80 if len(splitted_command) < 4 else splitted_command[3]
    ) + b'\r\n' + b'Connection: ' + b'keep-alive' + b'\r\n'

    if splitted_command[0] == b'GET':
        request = request + get_request_headers("GET") + b'\r\n'
    elif splitted_command[0] == b'POST':
        data = read_file(splitted_command[1].decode(encoding='UTF-8'))
        request = request + b'Content-Type: ' + get_content_type(splitted_command[1].decode(encoding='UTF-8')) + b'\r\n'
        request = request + b'Content-Length:  ' + str(len(data)).encode() + b'\r\n'
        request = request + get_request_headers("POST") + b'\r\n'
        request = request + data + b'\r\n'
    return request


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
