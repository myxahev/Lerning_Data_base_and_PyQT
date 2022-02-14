from subprocess import call, Popen
import threading


def create_client():
    COMMAND = "messager\client.py"
    Popen(COMMAND, shell=False)


def start_clients(qty: int):
    threads = []
    for i in range(qty):
        threads.append(threading.Thread(target=create_client))
        threads[i].start()
    return threads


def start_two_clients():
    start_clients(2)


def start_server():
    COMMAND = "messager\server.py"
    call(COMMAND, shell=False)


if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    threading.Thread(target=start_two_clients).start()
