"""Утилиты"""

import json
from decors import Log
import json
import os
import sys
import yaml

def_path = os.getcwd()

with open(def_path + '\messager\config.yaml', encoding='utf-8') as conf_file:
    data = yaml.load(conf_file, Loader=yaml.FullLoader)


@Log()
def get_message(socket):
    response_encoded = socket.recv(data['MAX_PACKAGE_LENGTH'])
    if isinstance(response_encoded, bytes):
        response_json = response_encoded.decode(data['ENCODING'])
        response = json.loads(response_json)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@Log()
def send_message(socket, message):
    message_json = json.dumps(message)
    message_encoded = message_json.encode(data['ENCODING'])
    socket.send(message_encoded)