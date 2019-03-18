from socket import socket, AF_INET, SOCK_STREAM, error
import queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as Et
import time

import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT, filename="/tmp/updating_cameras_events.log", level=logging.INFO)
log = logging.getLogger()

# creating queue instance
q = queue.Queue()


class SocketClientThread(Thread):

    # def __init__(self, _host="127.0.0.1", _port=44000):
    def __init__(self, _host="192.168.0.108", _port=44000):
        Thread.__init__(self)
# test
#         self.sdata = '''<CitiEvent Type="LIFESIG"> \
# <LIFESIG PeriodSec="30" TimeOutSec="60" /> \
# </CitiEvent>'''
        # self.sdata = '''<CitiEvent Type="Alarm"><Alarm Id="159612"> \
# <Type>StopC</Type><CameraName>Camera 13</CameraName><CameraId>13</CameraId> \
# <LaneId>2</LaneId><StartTime>2019/01/28 21:25:15</StartTime> \
# <EndTime>2019/01/28 21:26:58</EndTime> \
# <Comment></Comment><VideoClipName>C13_AXIS_28012019_202445_StopC.seq</VideoClipName> \
# <RowRatio>21</RowRatio><ColumnRatio>269</ColumnRatio></Alarm></CitiEvent>'''
        self.host = _host
        self.port = _port
        self.sock = socket(AF_INET, SOCK_STREAM)

    @staticmethod
    def get_text(obj, name):
        _obj = obj.find(name)
        return _obj.text if type(_obj) != 'NoneType' else ""

    def run(self):

        # global results
        size = 65535
        with self.sock as _socket:
            # Connect to server and send data
            _socket.connect((self.host, self.port))
            # _socket.sendall(bytes(self.sdata, encoding='utf-8', errors='ignore'))
            while True:
                try:
                    data = _socket.recv(size).decode('utf8', errors='ignore')
                    if not data:
                        raise error('Client disconnected')
                    else:
                        data = "<root>" + data + "</root>"

                    log.info("!!! xml client get values: \n {}".format(str(data)))

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
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(SocketClientThread().start())
        echo = ['0']*11
        while not q.empty():
            results = q.get()
            if results:
                echo = results
            print(echo)
        time.sleep(3)

