from sockwrapper.socket_wrapper import SocketWrapper
import socket


class ClientConnection(object):
    def __init__(self, host, port, ipv6=False, timeout=0.5, recv_filename=None, send_filename=None):
        # self.recv_f = open(recv_filename, "ba")
        # self.send_f = open(send_filename, "ba")
        self.conn = SocketWrapper(
            family=socket.AF_INET6 if ipv6 else socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
        self.conn.settimeout(timeout)
        self.conn.connect((host, port))

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        # self.recv_f.close()
        # self.send_f.close()