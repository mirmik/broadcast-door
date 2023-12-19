#!/usr/bin/env python3

import socket 
import string
import random
import subprocess
import os
import base64 as b64

broadcast_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
broadcast_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

broadcast_server.bind(('', 11722))

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))

def get_unique_id():
    unique_id_fname = ".broadcast_shell_unique_id"
    unique_id_path = os.path.join("~", unique_id_fname)
    unique_id_path = os.path.expanduser(unique_id_path)
    if os.path.exists(unique_id_path):
        with open(unique_id_path, 'r') as f:
            unique_id = f.read()
    else:
        unique_id = random_string(20)
        with open(unique_id_path, 'w') as f:
            f.write(unique_id)
    return unique_id

unique_id = get_unique_id()

print ("Unique ID: " + unique_id)

def execute_personal(cmd):
    print('Received personal message: ' + msg)
    
    try:
        # execute command
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        output = b64.b64encode(output)
        error = b64.b64encode(error)

        # send output
        answer = "answer|" + str(unique_id) + "|" + output.decode('utf-8') + "|" + error.decode('utf-8')
        broadcast_server.sendto(answer.encode("utf-8"), ('<broadcast>', 11722))
    except Exception as e:
        print(e)
        answer = "answer|" + str(unique_id) + "|" + str(e)
        broadcast_server.sendto(answer.encode("utf-8"), ('<broadcast>', 11722))


def execute(msg):
    if msg == 'ping':
        answer = 'pong|' + str(unique_id)
        broadcast_server.sendto(answer.encode("utf-8"), ('<broadcast>', 11722))

    if msg.startswith(unique_id):
        msglst = msg.split('|')
        msglst.pop(0)
        msg = '|'.join(msglst)
        execute_personal(msg)

while True:
    data, addr = broadcast_server.recvfrom(1024)
    print("Received from %s: %s" % (addr, data))

    msg = data.decode('utf-8')
    execute(msg)
