from socket import socket, AF_INET, SOCK_STREAM, error
import threading
import xml.etree.ElementTree as Et


class SocketClientThread(threading.Thread):
    def __init__(self, _host, _port):
        threading.Thread.__init__(self)
        self.host = _host
        self.port = _port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def run(self):
        global results
        size = 65535
        # print("Starting Client (listing to port %d %s)" % (self.port, self.host))
        with self.sock as _socket:
            while True:
                try:
                    data = _socket.recv(size).decode('utf8', errors='ignore')
                    if not data:
                        raise error('Client disconnected')
                    else:
                        data = "<root>" + data + "</root>"

                    tree = Et.XMLParser(encoding="utf-8")
                    tree = Et.fromstring(data, parser=tree)

                    if not tree:
                        raise error('Not an XML tree')

                    for root in tree.findall('CitiEvent'):
                        if root.get('Type') == "Device":
                            for device in root.findall('Device'):
                                _type = device.find('Type')
                                if type(_type) != 'NoneType' and _type.text == "Camera":
                                    _type = _type.text
                                    _name = device.find('Name').text
                                    _addr = device.find('Address').text
                                    _state = device.find('State').text
                                    _camera_id = device.find('CameraId').text
                                    _camera_name = device.find('CameraName').text
                                    # print(_name, _type, _addr, _state, _camera_id, _camera_name)
                                    # yield _name, _type, _addr, _state, _camera_id, _camera_name
                                    results = [_name, _type, _addr, _state, _camera_id, _camera_name]

                except (ConnectionResetError, error) as e:
                    # print(e)
                    break

                except Exception as ex:
                    # print(ex)
                    break


if __name__ == "__main__":
    host = "10.1.1.12"
    port = 44000
    results = []
    while True:
        th = SocketClientThread(host, port)
        th.start()
        echo = ['0', '0', '0', '0', '0', '0']
        if results:
            echo = results
        print(echo)
