from posixpath import split
import socket
from requests import head
import os
import sys

HTTP_VERSION = "HTTP/1.1"
SERVER_IP = "127.0.0.1"
HTTP_PORT = 80
BUFFER_SIZE = 2048

def client(command_file):
    commands = read_command(command_file)
    for command in commands:
        execute_command(generate_http_request(command))


def read_command(command_file):
    commands = None
    with open(command_file, mode='w') as file:
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
        request = request + 'Content-Type: ' + ''
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
        return ContentType
    elif file_extension == '.html':
        return 'text/html'
    elif file_extension == '.txt':
        return 'text/plain'

def read_file(file_name):
    file_content = None
    with open(file_name, mode='r') as file:
        file_content = file.read()

    return file_content

if __name__ == "__main__":
    client(sys.argv[0])




dir_path = "/media/ahmad/New Volume/8th term/network/Ass/Multi-threaded-web-server/Data/"

#READ COMMANDS FROM I/P FILES 
def open_commands_file():    
    f = open("commands.txt" , "r")
    return f
    

#TAKE PARSED COMMAND AND CONNECT TO THE SERVER 
#IF GET REQ. ONLY SEND HEADER AND SOME INFO 
#IF POST REQ. EXTRA PART WILL BE SEND (MESSAGE BODY)
def send_request(parsed_command, client):
    host_number = parsed_command[2]
    port_number = parsed_command[3]

#SET PORT NUMBER BY IT'S DEFAULT VALUE 80
    if port_number == "NULL":
        port_number = 80

    client.connect(host_number , port_number)
    info = "HOST: localhost \r\n"
    extra = "connection: keep_alive\r\n"

    #SEND POST REQUEST AND SEND PACKET TO SERVER
    if parsed_command[0] == "POST":
        header = parsed_command[0] + " /" + "HTTP1.1\r\n"
        message = get_message()
        message = message + "\r\n"
        send_message = header + info + extra + message
        client.sendall(send_message.encoded('utf-8'))

    #SEND GET REQUEST AND GET PACKET FROM SERVER
    else:
        header = parsed_command[0] + " /" + parsed_command[1] + " /" + "HTTP1.1\r\n"
        send_message = header + info + extra
        client.sendall(send_message.encoded('utf-8'))
        
    recived_pack = client.recv(2048)
    return recived_pack
        

#WILL TAKE THE MESSAGE WHICH WILL BE SEND TO send_request() FUNCTION
#TO ADD IT IN CASE POST REQ.
def get_message():
    filename_ = input("Enter the file name: ")
    with open(dir_path + filename , 'rb') as h:
        data = h.read()
    return "filename: " + filename_ + "\r\n" + "data: " + data

#CREATE SOCKET TO START CONNECTION WITH THE SERVER 
#REQ: SEND HOST AND PORT NUMBERS THAT WILL BE COMPATIABLE WITH SERVER
#PORT_NUMBER OF SERVER
#PARES THEM TO GET INFO
#COMMANDS: GET AND POST ONLY
#FORMAT: EX- GET FILENAME HOSTNAME (PORT-NUMBER)
#FLAG == 1 "MEANS TAKE COMMAND FROM I/P FILES"  ELSE TAKE IT FROM BASH
def run_client_host():
    print("enter 1 for bash command or 2 for file command: ")
    flag = input()                                          
    c_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    #IF COMMAND TAKEN FROM FILE 
    if flag == 1:
        f = open_commands_file() 
        command = f.readline()
    else:
        command = bash_commands()
    
    while command != "":
        parsed_command = command.split(" ")
        data = send_request(parsed_command , c_socket)
        store_data(data)
        command = f.readline()
    
    c_socket.close()

def bash_commands():
    command = input("Enter the command: ")

#TODO: DISPLAY RETURENED DATA AND STORE THEM IN THE DIRECTORY
#REQ. TO PARSE RESPONCE TO GET ACK , STATUS AND MESSAGE IF GET 
def store_data(responce):

    #PARSING THE RESPOCE TO GET THE INFO.
    if extention == "html":
        pass
    elif extention == "jpg" or extention == "png" or extention == "jpeg":
        pass
    else:
        pass




