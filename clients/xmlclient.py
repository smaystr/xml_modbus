from socket import socket, AF_INET, SOCK_STREAM, error
import queue
import threading
import xml.etree.ElementTree as Et

# creating queue instance
q = queue.Queue()


class SocketClientThread(threading.Thread):
    def __init__(self, _host="10.1.1.12", _port=44000):
        threading.Thread.__init__(self)
        self.host = _host
        self.port = _port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def run(self):
        # global results
        size = 65535
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
                                    q.put([_name, _type, _addr, _state, _camera_id, _camera_name])
                        if root.get('Type') == "Alarm":
                            for alarm in root.findall('Alarm'):
                                _alarm_id = alarm.get('Id')
                                _type = alarm.find('Type')
                                if type(_type) != 'NoneType':
                                    _type = _type.text
                                    _camera_name = alarm.find('CameraName').text
                                    _camera_id = device.find('CameraId').text
                                    _lane_id = device.find('LaneId').text
                                    _start_time = device.find('StartTime').text
                                    _end_time = device.find('EndTime').text
                                    _comment = device.find('Comment').text
                                    _video_clip_name = device.find('VideoClipName').text
                                    _row_ratio = device.find('RowRatio').text
                                    _column_ratio = device.find('ColumnRatio').text
                                    q.put([_alarm_id, _type, _comment, _video_clip_name, _camera_id, _camera_name,
                                           _lane_id, _start_time, _end_time,
                                           _row_ratio, _column_ratio])
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
        echo = ['0', '0', '0', '0', '0', '0']
        results = q.get()
        if results:
            echo = results
        print(echo)
