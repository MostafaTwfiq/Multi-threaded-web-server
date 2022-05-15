import socket
import os
from threading import *
import webbrowser
import sys
from datetime import datetime

cached_files = []
opened_connections = {}  # label: requests_queue

HTTP_VERSION = b'HTTP/1.1'
SERVER_IP = b'127.0.0.1'
BUFFER_SIZE = 4096
DATA_PATH = 'client_data'
CACHE_PATH = 'cache'
LOG_PATH = "client_log.txt"
time = datetime.now()

def commands_exec_thread(host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        requests_queue = []
        sent_requests_queue = []
        opened_connections[host] = requests_queue
        ip, port = host.split(':')
        # TODO: This can throw exception. Consider handling it.
        try:
            s.connect((ip, int(port)))
            write_log_file(f"Connection to Host Name {ip} and Port Number {port}")
            rec_resp_thread = Thread(target=receive_responses_thread, args=(s, sent_requests_queue, host))
            rec_resp_thread.start()

            while True:
                if len(requests_queue) > 0:
                    request = requests_queue.pop(0)
                    method, file_name, _ = request.split(b' ', 2)
                    try:
                        write_log_file(f"Sending to Host Name {ip} and Port Number {port} with method {method}")
                        s.sendall(request)
                    except:
                        break
                    sent_requests_queue.append([method.decode(), file_name.decode()])
        except:
            print("Connection Error Host Name Not Found")

    del opened_connections[host]


def receive_responses_thread(conn, sent_requests_queue, host):
    with conn:
        message = b''
        while True:
            data = conn.recv(BUFFER_SIZE)
            if len(data) == 0:
                break
            message += data
            message, response_dict = parse_http_response(message, sent_requests_queue[0][0])
            if response_dict is not None:
                write_log_file(f"Receiving request from Host Name {host}")
                execute_response(response_dict, sent_requests_queue.pop(0), host)


def get_file_if_cached(command):
    splitted_command = command.split(' ')
    method = splitted_command[0]
    file_path = splitted_command[1]
    ip = splitted_command[2]
    port = 80 if len(splitted_command) < 4 else splitted_command[3]
    cached_file_key = ip + ':' + str(port) + '-' + file_path
    if method == 'GET' and cached_file_key in cached_files:
        return file_path, read_file(file_path, True)

    return None, None


def client(command_file):
    commands = read_commands(command_file)
    for command in commands:
        # Check if the file is cached.
        file_path, file_data = get_file_if_cached(command)
        if file_data is not None:
            # TODO: check if we need to handle the case that the generating requests loop is faster than the real
            #  sending of them, which may deficit the job of the cache,
            store_file(file_path, file_data)
            continue

        # The file is not cached, create new response.
        request, ip, port = generate_http_request(command)
        host = ip + ':' + port
        if host not in opened_connections:
            comm_exec_thread = Thread(target=commands_exec_thread, args=(host, ))
            comm_exec_thread.start()
            while host not in opened_connections:
                continue

        opened_connections[host].append(request)


def read_commands(command_file):
    commands = None
    with open(command_file, mode='r') as file:
        commands = file.read().split('\n')
    return commands


def execute_response(response_dict, method_and_file, host):
    if method_and_file[0] == 'GET' and response_dict['response_code'] == '200':
        store_file(method_and_file[1], response_dict['file_data'])
        # Cache the file and added to the cached files data structure.
        store_file(method_and_file[1], response_dict['file_data'], True, False)
        cached_files.append(host + '-' + method_and_file[1])


def parse_http_response(data, method):  # data must be bytes
    if b'\r\n\r\n' not in data:
        return data, None

    response, remaining_data = data.split(b'\r\n\r\n', 1)
    start_line, headers = response.split(b'\r\n', 1)
    # parsing headers
    response_dict = {}
    splinted_headers = headers.split(b'\r\n')
    for curr_header in splinted_headers:
        header_name, header_val = curr_header.split(b':', 1)
        response_dict[header_name.decode()] = header_val.decode()
    # parsing first line
    splitted_start_line = start_line.split(b' ', 2)
    response_dict['http_version'] = splitted_start_line[0].decode()
    response_dict['response_code'] = splitted_start_line[1].decode()
    response_dict['response_state'] = splitted_start_line[2].decode()
    if method == 'GET':
        file_length = int(response_dict['Content-Length'])
        if file_length <= len(remaining_data):
            response_dict['file_data'] = remaining_data[0:file_length:1]
            if len(remaining_data) - file_length == 0:
                remaining_data = b''
            else:
                remaining_data = remaining_data[file_length:len(remaining_data):1]
        else:
            return data, None

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
        request = request + b'Content-Length: ' + str(len(data)).encode() + b'\r\n'
        request = request + get_request_headers("POST") + b'\r\n'
        request = request + data

    return request, ip.decode(), port.decode()


# TODO: Remove this or nazel elly fo2 hna zy ma tifa 3ayz.
def get_request_headers(method):
    if method == 'GET':
        return b''
    elif method == 'POST':
        return b''


def get_content_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == '.png':
        return b'image/png'
    elif file_extension == '.html':
        return b'text/html'
    elif file_extension == '.txt':
        return b'text/plain'


def store_file(file_name, file_data, in_cache=False, open_file=True):
    path = CACHE_PATH if in_cache else DATA_PATH
    file_path = path + os.sep + file_name
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode='wb') as file:
        file.write(file_data)

    if open_file:
        webbrowser.open(os.path.realpath(file_path))


def read_file(file_name, from_cache=False):
    file_content = None
    path = CACHE_PATH if from_cache else DATA_PATH
    file_path = path + os.sep + file_name
    with open(file_path, mode='rb') as file:
        file_content = file.read()

    return file_content

def write_log_file(msg):
    current_time = time.strftime("%H:%M:%S")
    with open(LOG_PATH, mode='a') as file:
        file.write(current_time + '\r')
        file.write(msg + '\r\n')


if __name__ == "__main__":
    client(sys.argv[1])
