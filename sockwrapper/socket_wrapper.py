import socket


class SocketWrapperException(Exception):
    pass


class ConnectionLostException(Exception):
    pass


class SocketWrapper(socket.socket):
    RECV_SIZE = 4096
    MAX_BUFF_SIZE = 1 << 22

    def __init__(self, *args, **kwargs):
        super(SocketWrapper, self).__init__(*args, **kwargs)
        self._buff = bytes()

    def send_line(self, msg: bytes, end=b"\n"):
        self.sendall(msg + end)

    def recv_until(self, seq: bytes, max_buf_size=MAX_BUFF_SIZE):
        while len(self._buff) <= max_buf_size and seq not in self._buff:
            data = self.recv(self.RECV_SIZE)
            if not data:
                raise ConnectionLostException("Connection lost")
            self._buff += data
        if len(self._buff) > max_buf_size:
            raise SocketWrapperException("Buff size is too big")
        found_pos = self._buff.find(seq)
        res = self._buff[:found_pos]
        self._buff = self._buff[found_pos + len(seq):]
        return res

