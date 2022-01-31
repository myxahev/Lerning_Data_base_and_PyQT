# Логгерский конфиг для сервера

import sys
import os
import logging
import lesson_8.common.variables as variables

LOG_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), variables.LOG_DIRECTORY)
LOG_FILE = os.path.join(LOG_DIRECTORY, variables.LOG_SERVER_NAME)

LOGGER = logging.getLogger('server')
LOGGER.setLevel(logging.DEBUG)

FORMAT = logging.Formatter('%(asctime)-10s %(levelname)-10s %(filename)-10s %(message)s')

STDERR_HANDLER = logging.StreamHandler(sys.stderr)
STDERR_HANDLER.setLevel(logging.INFO)
STDERR_HANDLER.setFormatter(FORMAT)

FILE_HANDLER = logging.FileHandler(LOG_FILE)
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMAT)

LOGGER.addHandler(STDERR_HANDLER)
LOGGER.addHandler(FILE_HANDLER)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
    LOGGER.warning('Внимание')