import socket
import os
import sys

HTTP_VERSION = b'HTTP/1.1'
SERVER_IP = b'127.0.0.1'
HTTP_PORT = 80
BUFFER_SIZE = 4096
PATH = "client_data"


def client(command_file):
    commands = read_command(command_file)
    for command in commands:
        execute_command(command)


def read_command(command_file):
    commands = None
    with open(command_file, mode='r') as file:
        commands = file.read().split('\n')
    return commands


def execute_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, HTTP_PORT))
        s.sendall(generate_http_request(command))
        response = b''
        while True:
            data = s.recv(BUFFER_SIZE)
            if len(data) == 0:
                break
            response += data

        print(response.decode())
        # TODO: if the request where GET then we need to write the data to disk.

        s.close()


def generate_http_request(command):
    command = command.encode(encoding='UTF-8')
    request = b''
    splitted_command = command.split(b' ')
    request = request + splitted_command[0] + b' ' + splitted_command[1] + b' ' + HTTP_VERSION + b'\r\n'
    request = request + b'HOST: ' + splitted_command[2] + b':' + bytes(
        80 if len(splitted_command) < 4 else splitted_command[3]
    ) + b'\r\n'

    if splitted_command[0] == b'GET':
        request = request + get_request_headers("GET") + b'\r\n'
    elif splitted_command[0] == b'POST':
        data = read_file(splitted_command[1].decode(encoding='UTF-8'))
        request = request + b'Content-Type: ' + get_content_type(splitted_command[1].decode(encoding='UTF-8')) + b'\r\n'
        request = request + b'Content-Length:  ' + str(len(data)).encode() + b'\r\n'
        request = request + get_request_headers("POST") + b'\r\n'
        request = request + data
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


def read_file(file_name):
    file_content = None
    file_path = PATH + os.sep + file_name
    print(file_path)
    with open(file_path, mode='rb') as file:
        file_content = file.read()

    return file_content


if __name__ == "__main__":
    #client(sys.argv[1])
    client('commands.txt')
