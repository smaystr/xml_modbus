from socket import socket, AF_INET, SOCK_STREAM, error
import queue
import threading
import xml.etree.ElementTree as Et

# creating queue instance
q = queue.Queue()


class SocketClientThread(threading.Thread):

    def __init__(self, _host="192.168.0.108", _port=44000):

        threading.Thread.__init__(self)
        self.host = _host
        self.port = _port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    @staticmethod
    def get_text(obj, name):
        _obj = obj.find(name)
        return _obj.text if type(_obj) != 'NoneType' else ""

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
                                _type = self.get_text(device, 'Type')
                                _name = self.get_text(device, 'Name')
                                _addr = self.get_text(device, 'Address')
                                _state = self.get_text(device, 'State')
                                _camera_id = self.get_text(device, 'CameraId')
                                _camera_name = self.get_text(device, 'CameraName')
                                q.put([_name, _type, _addr, _state, _camera_id, _camera_name])

                        if root.get('Type') == "Alarm":
                            for alarm in root.findall('Alarm'):
                                _alarm_id = alarm.get('Id')
                                _type = self.get_text(alarm, 'Type')
                                _camera_name = self.get_text(alarm, 'CameraName')
                                _camera_id = self.get_text(alarm, 'CameraId')
                                _lane_id = self.get_text(alarm, 'LaneId')
                                _start_time = self.get_text(alarm, 'StartTime')
                                _end_time = self.get_text(alarm, 'EndTime')
                                _comment = self.get_text(alarm, 'Comment')
                                _video_clip_name = self.get_text(alarm, 'VideoClipName')
                                _row_ratio = self.get_text(alarm, 'RowRatio')
                                _column_ratio = self.get_text(alarm, 'ColumnRatio')
                                q.put([_alarm_id, _type, _comment, _video_clip_name, _camera_id, _camera_name,
                                       _lane_id, _start_time, _end_time, _row_ratio, _column_ratio])
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
        echo = ['0']*11
        results = q.get()
        if results:
            echo = results
        print(echo)
        th.join(timeout=1)
