import json
import email
import pprint
from io import StringIO
import base64


import socket
import sys
import requests

if __name__ == '__main__':

    b = b'HTTP/1.1 200 OK\r\n'
    split = b.split(b' ', 2)
    print(split)



    #r = requests.get('https://xkcd.com/1906/')
    #print(r.json())
    #print(r.headers)

    '''api = 'http://localhost:80'
    image_file = 'sample_image.png'

    with open(image_file, "rb") as f:
        im_bytes = f.read()
    im_b64 = base64.b64encode(im_bytes).decode("utf-8")
    print(im_b64)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    payload = json.dumps({"image": im_b64, "other_key": "value"})
    response = requests.post(api, data=payload, headers=headers)
    print(response.text)

    request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\nmostafa" % '127.0.0.1:80'
    request = request.encode(encoding='UTF-8')

    # Convert bytes to string type and string type to dict
    string = request.decode('utf-8')
    start_line, headers = string.split('\r\n', 1)
    data = 'aa'
    splitted = headers.split('\r\n')
    #print(splitted)
    for i, h in enumerate(splitted):
        if h == '' and i < len(splitted) - 1:
            data = splitted[i + 1]
            break

    #print(data)
    #print()
    #print(headers)

    # construct a message from the request string
    message = email.message_from_file(StringIO(headers.replace('\r\n\r\n', '\r\ndata:')))
    print(message)

    # construct a dictionary containing the headers
    headers = dict(message.items())
    print(headers)'''
    # pretty-print the dictionary of headers
    #pprint.pprint(headers, width=160)
    #print(json_obj['source_name'])  # prints the string with 'source_name' key'''

    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))

    # default port for socket
    port = 80

    try:
        host_ip = socket.gethostbyname('www.google.com')
        print(host_ip)
    except socket.gaierror:

        # this means could not resolve the host
        print("there was an error resolving the host")
        sys.exit()

    # connecting to the server
    s.connect((host_ip, port))

    print("the socket has successfully connected to google")'''