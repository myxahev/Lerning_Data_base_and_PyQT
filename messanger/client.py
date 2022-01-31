# client

# import data.variables as variables
from data.utils import get_message, send_message
import errors_user as errors_user

import yaml
import sys
import json
import socket
import time
import argparse
import logging
from decors import Log
import threading
import os

def_path = os.getcwd()

with open(def_path + '\messager\config.yaml', encoding='utf-8') as conf_file:
    data = yaml.load(conf_file, Loader=yaml.FullLoader)

LOG = logging.getLogger('client')


class Client:

    @Log(LOG)
    def __init__(self):
        self.server_port, self.server_address, self.client_name = self.get_params()
        self.transport = self.prepare_transport()

    @Log(LOG)
    def create_presence_msg(self, action, message=None, destination=None):
        result_message = {
            data['ACTION']: action,
            data['TIME']: time.time(),
            data['PORT']: self.server_port,
        }

        if action == data['PRESENCE']:
            result_message[data['USER']] = {data['ACCOUNT_NAME']: self.client_name}

        elif action == data['MESSAGE'] and message and destination:
            result_message[data['SENDER']] = self.client_name
            result_message[data['MESSAGE_TEXT']] = message
            result_message[data['DESTINATION']] = destination

        elif action == data['EXIT']:
            result_message[data['ACCOUNT_NAME']] = self.client_name

        return result_message

    @Log(LOG)
    def server_process_answer(self):
        server_message = get_message(self.transport)
        if data['RESPONSE'] in server_message:
            if server_message[data['RESPONSE']] == 200:
                return '200 : OK'
            return f'400 : {server_message[data["ERROR"]]}'
        raise errors_user.NoResponseInServerMessageError

    def process_server_message(self):
        while True:
            try:
                server_message = get_message(self.transport)
                if server_message.get(data['ACTION']) == data['MESSAGE'] and \
                        data['SENDER'] in server_message and data['MESSAGE_TEXT'] in server_message and \
                        server_message.get(data['DESTINATION']) == self.client_name:
                    LOG.debug(f'{self.client_name}: Получено сообщение от {server_message[data["SENDER"]]}')
                    print(f'\n<<{server_message[data["SENDER"]]}>> : {server_message[data["MESSAGE_TEXT"]]}')

                elif server_message.get(data['ACTION']) == data['MESSAGE'] and \
                        data['SENDER'] in server_message and data['MESSAGE_TEXT'] in server_message and \
                        server_message.get(data['DESTINATION']) != self.client_name:
                    LOG.debug(f'{self.client_name}: Получено сообщение от {server_message[data["SENDER"]]}')
                    print(f'\n<<{server_message[data["SENDER"]]}>> : {server_message[data["MESSAGE_TEXT"]]}')
                else:
                    LOG.debug(f'{self.client_name}: Получено сообщение от сервера о некорректном запросе')
                    print(f'\nПолучено сообщение от сервера о некорректном запросе: {server_message}')
            except errors_user.IncorrectDataRecivedError as error:
                LOG.error(f'Ошибка: {error}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOG.critical(f'Потеряно соединение с сервером.')
                break

    @Log(LOG)
    def message_from_server(self, to_client, message):
        message_to_send = self.create_presence_msg(data['MESSAGE'], message, to_client)
        try:
            send_message(self.transport, message_to_send)
            LOG.info(f'{self.client_name}: Отправлено сообщение для пользователя {to_client}')
        except Exception:
            LOG.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @Log(LOG)
    def prepare_transport(self):
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((self.server_address, self.server_port))
        except ConnectionRefusedError:
            LOG.critical(f'Не удалось подключиться к серверу {self.server_address}:{self.server_port}')
            sys.exit(1)
        return transport

    def user_interactive(self):
        self.print_help()
        while True:
            command = input('Введите команду: ').lower()
            if command == 'message':
                self.message_from_server(*self.input_message())
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                send_message(self.transport, self.create_presence_msg(data['EXIT']))
                print('Завершение соединения.')
                LOG.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @Log(LOG)
    def send_presence(self):
        try:
            send_message(self.transport, self.create_presence_msg(data['PRESENCE']))
            answer = self.server_process_answer()
            LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
            return True if answer == '200 : OK' else False
        except json.JSONDecodeError:
            LOG.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except errors_user.NoResponseInServerMessageError as error:
            LOG.error(f'Ошибка сообщения сервера {self.server_address}: {error}')

    def run(self):
        print(self.client_name)
        if self.send_presence():
            receiver = threading.Thread(target=self.process_server_message)
            receiver.daemon = True
            receiver.start()

            user_interface = threading.Thread(target=self.user_interactive)
            user_interface.daemon = True
            user_interface.start()
            LOG.debug(f'{self.client_name}: Запущены процессы')

            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break

    @staticmethod
    @Log(LOG)
    def print_help():
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    @staticmethod
    @Log(LOG)
    def input_message():
        while True:
            to_client = input('Введите имя пользователя-адресата, чтобы отправить личное сообщние или оставьте пустым, чтобы отправить в общий чат:')
            message = input('Введите сообщение:')
            if to_client.strip() and message.strip():
                break
            elif not to_client:
                to_client = ' '
                break
            elif not message:
                message = ' '
                break
            elif not message and not to_client:
                message = ' '
                to_client = ' '
                break
        return to_client, message

    @staticmethod
    @Log(LOG)
    def get_params():
        parser = argparse.ArgumentParser()
        parser.add_argument('port', nargs='?', type=int, default=data['DEFAULT_PORT'])
        parser.add_argument('address', nargs='?', type=str, default=data['DEFAULT_IP_ADDRESS'])
        parser.add_argument('-n', '--name', type=str, default='Evgeny')

        args = parser.parse_args()

        server_port = args.port
        server_address = args.address
        client_name = args.name

        try:
            if not (1024 < server_port < 65535):
                raise errors_user.PortError
        except errors_user.PortError as error:
            LOG.critical(f'Ошибка порта {server_port}: {error}. Соединение закрывается.')
            sys.exit(1)
        return server_port, server_address, client_name


if __name__ == '__main__':
    client = Client()
    client.run()