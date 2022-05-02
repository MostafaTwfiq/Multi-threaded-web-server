from posixpath import split
import socket
from requests import head
import os
import sys

HTTP_VERSION = "HTTP/1.1"
SERVER_IP = "127.0.0.1"
HTTP_PORT = 80

def client(command_file):
    commands = read_command(command_file)
    for command in commands:
        execute_command(generate_http_request(command))


def read_command(command_file):
    commands = None
    with open(command_file, mode='r') as file:
        commands = file.read().split('\r\n')

    return commands


def execute_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, HTTP_PORT))
        s.sendall(generate_http_request(command).encode(encoding='UTF-8'))
        s.close()



def generate_http_request(command):
    request = ''
    splitted_command = command.split(' ')
    request = request + splitted_command[0] + splitted_command[1] + HTTP_VERSION + '\r\n'
    request = request + "HOST: " + SERVER_IP + ":" + HTTP_PORT + '\r\n'

    if splitted_command[0] == 'GET':
        request = request + get_request_headers("GET") + '\r\n\r\n'
    elif splitted_command[0] == 'POST':
        data = read_file(splitted_command[1])
        request = request + 'Content-Type: ' + get_content_type(splitted_command[1])
        request = request + 'Content-Length:  ' + str(len(data))
        request = request + get_request_headers("POST") + '\r\n\r\n'
        request = request + data

    return request

def get_request_headers(method):
    if method == "GET":
        return ''
    elif mathod == "POST":
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
    with open(file_name, mode='rb') as file:
        file_content = file.read()

    return file_content

if __name__ == "__main__":
    client(sys.argv[0])




