from socket import socket, AF_INET, SOCK_STREAM, error
from threading import Thread
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
import time


class SocketSignOfLifeThread(Thread):

    # def __init__(self, _host="127.0.0.1", _port=44000):
    def __init__(self, _host="192.168.0.108", _port=44000):

        Thread.__init__(self)
        self.data = '<CitiEvent Type="LIFESIG"><LIFESIG PeriodSec="30" TimeOutSec="60" /></CitiEvent>'
        self.host = _host
        self.port = _port
        self.sock = socket(AF_INET, SOCK_STREAM)

    def run(self):
        with self.sock as _socket:
            # Connect to server and send data
            _socket.connect((self.host, self.port))
            try:
                # print("Sent:     {}".format(self.data))
                _socket.sendall(bytes(self.data, encoding='utf-8', errors='ignore'))
                # Receive data from the server and shut down
                # received = str(_socket.recv(1024), "utf-8")
                # print("Received: {}".format(received))
            except (ConnectionResetError, error) as e:
                # print(e)
                pass
            except Exception as ex:
                # print(ex)
                pass


def client_run():
    while True:
        with ThreadPoolExecutor(max_workers=1) as spool:
            spool.submit(SocketSignOfLifeThread().start())
        time.sleep(30)


if __name__ == "__main__":
    p = Process(target=client_run)
    p.start()
    p.join()
