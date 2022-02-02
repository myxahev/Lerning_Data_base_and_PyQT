"""Утилиты"""

import yaml
from messanger.errors_user import IncorrectDataRecivedError, NonDictInputError
import json
import sys
import os

sys.path.append('../')
from messanger.decors import log
import logging

def_path = os.getcwd()
with open(def_path + '/config.yaml', encoding='utf-8') as conf_file:
    data = yaml.load(conf_file, Loader=yaml.FullLoader)

# LOGGING_LEVEL = logging.DEBUG


# Утилита приёма и декодирования сообщения
# принимает байты выдаёт словарь, если приняточто-то другое отдаёт ошибку значения
@log
def get_message(client):
    encoded_response = client.recv(data["MAX_PACKAGE_LENGTH"])
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(data["ENCODING"])
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


# Утилита кодирования и отправки сообщения
# принимает словарь и отправляет его
@log
def send_message(sock, message):
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(data["ENCODING"])
    sock.send(encoded_message)