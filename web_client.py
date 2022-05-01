import socket

from requests import head

#READ COMMANDS FROM I/P FILES 
def open_commands_file():    
    f = open("commands.txt" , "r")
    return f
    

#TAKE PARSED COMMAND AND CONNECT TO THE SERVER 
#IF GET REQ. ONLY SEND HEADER AND SOME INFO 
#IF POST REQ. EXTRA PART WILL BE SEND (MESSAGE BODY)
def send_request(parsed_command , client):
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
        
    recived_pack = client.recivefrom(2048)
        

#WILL TAKE THE MESSAGE WHICH WILL BE SEND TO send_request() FUNCTION
#TO ADD IT IN CASE POST REQ.
def get_message():
    return "hello! world"


#CREATE SOCKET TO START CONNECTION WITH THE SERVER 
#REQ: SEND HOST AND PORT NUMBERS THAT WILL BE COMPATIABLE WITH SERVER
#PORT_NUMBER OF SERVER
#PARES THEM TO GET INFO
#COMMANDS: GET AND POST ONLY
#FORMAT: EX- GET FILENAME HOSTNAME (PORT-NUMBER)
def run_client_host():
    c_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    f = open_commands_file() 
    command = f.readline()
    
    while command != "":
        parsed_command = command.split(" ")
        send_request(parsed_command , c_socket)
        command = f.readline()
    
    c_socket.close()

#TODO: DISPLAY RETURENED DATA AND STORE THEM IN THE DIRECTORY