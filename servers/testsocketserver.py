import threading
import socketserver


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = str(self.request.recv(1024).strip(), encoding='utf-8', errors='ignore')
        # data = '''<CitiEvent Type="Device"><Device><Name>Cam3</Name><Type>Camera</Type>
        # <Address>192.168.0.12</Address><State>OK</State><CameraId>3</CameraId>
        # <CameraName>Camera 3</CameraName></Device></CitiEvent>'''
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), encoding='utf-8')
        print("{} wrote: {}".format(self.client_address[0], data))
        # just send back the same data, but upper-cased
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "localhost", 44000

    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address
        server.serve_forever()
