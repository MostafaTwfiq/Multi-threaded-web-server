import socket
import os
import sys
import webbrowser

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
        file_name = command.split(' ')[1]
        s.connect((SERVER_IP, HTTP_PORT))
        s.sendall(generate_http_request(command))
        response = b''
        response_dict = {}
        while True:
            try:
                data = s.recv(BUFFER_SIZE)
                if len(data) == 0:
                    break
                response += data
                response_dict = parse_http_request(data=response)
                if len(response_dict['file_data']) == int(response_dict['Content-Length']):
                    break
                elif len(response_dict['file_data']) > int(response_dict['Content-Length']):
                    print("Error in data")
                    break
                if response_dict['Connection'] != 'keep-alive':
                    print('Connection is Closed')
                    break
                print(response_dict.keys())
            except:
                print('Connection Closed')
                break

        if int(response_dict['status']) == 200 and int(response_dict['Content-Length']) != 0:
            #save and open
            save_open_file(file_name, response_dict['file_data'])
        else:
            print(response.decode())
        s.close()

def parse_http_request(data): 
    response_dict = {}
    header, body = data.split(b'\r\n\r\n', 1)
    header_list = header.split(b'\r\n')
    response_dict['http_version'] = header_list[0].split(b' ')[0]
    response_dict['status'] = header_list[0].split(b' ')[1]
    for h in header_list:
        line = h.split(b' ')
        if b'Content-Length:' in line:
            response_dict['Content-Length'] = line[-1]
        elif b'Connection' in line:
            response_dict['Connection'] = line[-1]
    response_dict['file_data'] = body
    return response_dict

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
        request = request + b'Connection: '+b'keep-alive'+ b'\r\n'
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


def save_open_file(file_name, file_data):
    file_name = file_name
    file_path = PATH + os.sep + file_name
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
