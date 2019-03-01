from socket import socket, AF_INET, SOCK_STREAM, error
import queue
import threading
import time

# creating queue instance
q = queue.Queue()


class SocketClientThread(threading.Thread):

    def __init__(self, _host="10.1.1.12", _port=44000):

        threading.Thread.__init__(self)
        self.command = '<xml version="1.0" encoding="UTF-8"><header/><body><code><body/>'
        self.self.host = _host
        self.port = _port
        self.sock = socket(AF_INET, SOCK_STREAM)
        # print('create socket')
        self.sock.connect((self.host, self.port))
        # print('connect')

    def run(self):

        with self.sock as _socket:
            print("sock reading")
            while True:
                try:
                    _socket.send(self.command)
                    time.sleep(30)

                except (ConnectionResetError, error) as e:
                    # print(e)
                    break
                except Exception as ex:
                    # print(ex)
                    break


if __name__ == "__main__":
    while True:
        th = SocketClientThread()
        th.start()
