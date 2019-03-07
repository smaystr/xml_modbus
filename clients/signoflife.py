from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import time


class SocketSignOfLifeThread(Thread):
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
            # print("Sent:     {}".format(self.data))
            _socket.sendall(bytes(self.data, encoding='utf-8', errors='ignore'))
            # Receive data from the server and shut down
            # received = str(_socket.recv(1024), "utf-8")
            # print("Received: {}".format(received))


def client_run():
    while True:
        th = SocketSignOfLifeThread()
        th.start()
        th.join(timeout=1)
        time.sleep(30)


if __name__ == "__main__":
    tf = Thread(target=client_run)
    tf.start()
    tf.join(timeout=1)

