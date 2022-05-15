import os
import socket
from os import path
from threading import *
from datetime import datetime

resources_semaphore = Semaphore(1)
resources_dict = {}
count_semaphore = Semaphore(1)
MY_HOST = b'127.0.0.1'
MY_PORT = 2000
BUFFER_SIZE = 4096
sperator = b'\r\n'
STATUS_200 = b'HTTP/1.1 200 OK' + sperator
STATUS_404 = b'HTTP/1.1 404 Not Found' + sperator
PATH = "server_data"
LOG_PATH = "server_log.txt"
time = datetime.now()


def server():
    connections_count = [0]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((MY_HOST, MY_PORT))
        while True:
            s.listen()
            conn, addr = s.accept()
            conn_thread = Thread(target=conn_thread_fn, args=(conn, addr, connections_count))
            conn_thread.start()


def conn_thread_fn(conn, addr, conn_count):
    count_semaphore.acquire()
    conn_count[0] += 1
    count_semaphore.release()

    requests_queue = []
    conn_flag = [True]
    requests_thread = Thread(target=responses_thread_fn, args=(conn, requests_queue, conn_flag, addr))
    requests_thread.start()
    with conn:
        print(f"Connected by {addr}")
        write_log_file(f"Connected by {addr}")
        message = b''
        while True:
            try:
                # Receive HTTP MSG.
                conn.settimeout(timeout_heuristic(conn_count[0]))
                data = conn.recv(BUFFER_SIZE)
                conn.settimeout(None)
                message += data
                request_dict = 1
                while request_dict:
                    message, request_dict = parse_http_request(data=message)
                    if request_dict is not None:
                        write_log_file(
                            f"Received request from {addr}, with method {request_dict['method']}, and file {request_dict['file_name']}")
                        if (request_dict['http_version'] == 'HTTP/1.1' or request_dict['http_version'] == 'HTTP/1.0') and request_dict['connection'] == 'keep-alive':
                            requests_queue.append(request_dict)
                        else:  # In this case it may be http1.0 or even http1.1 with a Connection: close
                            server_result = get_response(request_dict)
                            http_response = write_http_respond(request_dict, server_result)
                            conn.sendall(http_response)
                            raise ValueError("closing")

            except Exception as e:
                if e == "closing":
                    write_log_file(f"Closing {addr} as it is a none persistent connection.")
                else:
                    write_log_file(f"A timeout occur in the connection {addr}")
                print(e)
                break

        conn.close()

        count_semaphore.acquire()
        conn_count[0] -= 1
        count_semaphore.release()

        conn_flag[0] = False


def responses_thread_fn(conn, requests_queue, conn_flag, addr):
    while conn_flag[0]:
        if len(requests_queue) > 0:
            request_dict = requests_queue.pop(0)
            server_result = get_response(request_dict)
            http_response = write_http_respond(request_dict, server_result)
            try:
                write_log_file(f"Sending response to {addr}, for the request with method {request_dict['method']}, "
                               f"and file {request_dict['file_name']}")
                conn.sendall(http_response)
                write_log_file(f"Response to {addr}, for the request with method {request_dict['method']}, "
                               f"and file {request_dict['file_name']} was sent successfully")
            except Exception as e:
                print(e)


def parse_http_request(data):  # data must be bytes
    if b'\r\n\r\n' not in data:
        return data, None

    request, remaining_data = data.split(b'\r\n\r\n', 1)
    start_line, headers = request.split(b'\r\n', 1)
    # parsing headers
    request_dict = {}
    splinted_headers = headers.split(b'\r\n')
    for curr_header in splinted_headers:
        header_name, header_val = curr_header.split(b':', 1)
        request_dict[header_name.decode().lower()] = header_val.lstrip().decode()
    # parsing first line
    splinted_start_line = start_line.split(b' ')
    request_dict['method'] = splinted_start_line[0].decode()
    request_dict['file_name'] = splinted_start_line[1].decode()
    request_dict['http_version'] = splinted_start_line[2].decode()
    if request_dict['method'] == 'POST':
        file_length = int(request_dict['content-length'])
        if file_length <= len(remaining_data):
            request_dict['file_data'] = remaining_data[0:file_length:1]
            if len(remaining_data) - file_length == 0:
                remaining_data = b''
            else:
                remaining_data = remaining_data[file_length:len(remaining_data):1]
        else:
            return data, None

    return remaining_data, request_dict


# Get status of the request
def get_response(message_dic):
    resources_semaphore.acquire()
    if message_dic['file_name'] not in resources_dict:
        resources_dict[message_dic['file_name']] = [Semaphore(1), Semaphore(1), 0]

    mutix, wrt_sem, readers = resources_dict[message_dic['file_name']]
    resources_semaphore.release()

    server_result = {}
    if message_dic['method'] == 'POST':
        # readers-writes semaphore
        wrt_sem.acquire()

        file_exist = store_file(message_dic['file_name'], message_dic['file_data'])

        wrt_sem.release()

        if file_exist:
            server_result['status'] = 200
        else:
            server_result['status'] = 404
    elif message_dic['method'] == 'GET':
        # readers-writer semaphore
        mutix.acquire()
        readers += 1
        resources_dict[message_dic['file_name']][
            2] = readers  # update readers count of the resource in the resources dictionary
        if readers == 1:
            wrt_sem.acquire()
        mutix.release()

        file_data = read_file(message_dic['file_name'])

        mutix.acquire()
        readers -= 1
        resources_dict[message_dic['file_name']][
            2] = readers  # update readers count of the resource in the resources dictionary
        if readers == 0:
            wrt_sem.release()

        mutix.release()

        if file_data:
            server_result['status'] = 200
            server_result['body'] = file_data
        else:
            server_result['status'] = 404

    return server_result


# Write Respond
def write_http_respond(message_dic, server_result):
    # For GET Requests
    if server_result['status'] == 200 and message_dic['method'] == 'GET':
        file = server_result['body']
        return STATUS_200 + b'Content-Length: ' + str(
            len(file)).encode() + sperator + b'Connection: keep-alive' + sperator + sperator + file
    # For POST Request
    elif server_result['status'] == 200 and message_dic['method'] == 'POST':
        return STATUS_200 + b'Content-Length: 0' + sperator + b'Connection: keep-alive' + sperator + sperator
    elif server_result['status'] == 404:
        return STATUS_404 + b'Content-Length: 0' + sperator + b'Connection: keep-alive' + sperator + sperator


# Store File on POST Request
def store_file(file_name, file_data):
    file_path = PATH + os.sep + file_name
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, mode='wb') as file:
        file.write(file_data)

    if not path.exists(file_path):
        return False
    return True


# Get file in GET Request
def read_file(file_name):
    file_content = None
    file_name = file_name
    file_path = PATH + os.sep + file_name
    try:
        with open(file_path, mode='rb') as file:
            file_content = file.read()
    except:
        return file_content
    return file_content


def timeout_heuristic(conn_count):
    return 10 * 1 / conn_count


def write_log_file(msg):
    current_time = time.strftime("%H:%M:%S")
    with open(LOG_PATH, mode='a') as file:
        file.write(current_time + '\r')
        file.write(msg + '\r\n')


if __name__ == "__main__":
    write_log_file(f'Server is now listening to the ip {MY_HOST} and Port {MY_PORT}')
    server()
