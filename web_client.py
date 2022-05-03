from posixpath import split
import socket
from requests import head
import os
import sys

HTTP_VERSION = "HTTP/1.1"
SERVER_IP = "127.0.0.1"
HTTP_PORT = 80
BUFFER_SIZE = 200000
PATH = "D:\desktop\eng\8thTerm\CN\Multi-threaded-web-server\client_data\\"
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
        response = ''
        while True:
            data = s.recv(BUFFER_SIZE)
            if len(data) == 0:
                break
            response += data.decode()

        print(response)
        #TODO: if the request where GET then we need to write the data to disk.

        s.close()

def generate_http_request(command):
    request = ''
    splitted_command = command.split(' ')
    request = request + splitted_command[0] + " " + splitted_command[1] + " " + HTTP_VERSION + '\r\n'
    request = request + "HOST: " + splitted_command[2] + ":" + str(80 if len(splitted_command) < 4 else splitted_command[3]) + '\r\n'

    if splitted_command[0] == 'GET':
        request = (request + get_request_headers("GET") + '\r\n').encode()
    elif splitted_command[0] == 'POST':
        data = read_file(splitted_command[1])
        request = request + 'Content-Type: ' + get_content_type(splitted_command[1])
        request = request + 'Content-Length:  ' + str(len(data))
        request = request + get_request_headers("POST") + '\r\n\r\n'
        request = request.encode() + data
    return request

def get_request_headers(method):
    if method == "GET":
        return ''
    elif method == "POST":
        return ''

def get_content_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == '.png':
        return 'image/png'
    elif file_extension == '.html':
        return 'text/html'
    elif file_extension == '.txt':
        return 'text/plain'

def read_file(file_name):
    file_content = None
    file_path = PATH + '\\' + file_name
    with open(file_path, mode='rb') as file:
        file_content = file.read()

    return file_content

if __name__ == "__main__":
    client(sys.argv[1])




