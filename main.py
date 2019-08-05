#! /usr/bin/env python3

import argparse
import curses
import json
import logging
import threading
import sys

import nclib.netcat

key_to_direction = {
    'w': 'up',
    'a': 'left',
    's': 'down',
    'd': 'right',
}

WIDTH = 51
HEIGHT = 51
DEFAULT_PORT = 34131


class CommandSenderThread(threading.Thread):
    def __init__(self, scr, conn):
        super(CommandSenderThread, self).__init__()
        self._scr = scr
        self._conn = conn

    def run(self):
        while True:
            key = self._scr.getch()
            curses.flushinp()
            if key == ord('q'):
                return
            direction = key_to_direction.get(chr(key), None)
            if direction is not None:
                self._conn.send_line(json.dumps({"direction": direction}).encode(), ending=b'\n')


class Connection(object):
    def __init__(self, host, port, recv_filename, send_filename):
        # self.recv_f = open(recv_filename, "ba")
        # self.send_f = open(send_filename, "ba")
        self.conn = nclib.netcat.Netcat(
            connect=(host, port),
            verbose=False,  # Don't set it
            # log_recv=self.recv_f,
            # log_send=self.send_f,
            raise_timeout=True,
        )
        self.conn.echo_hex = True

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        # self.recv_f.close()
        # self.send_f.close()


def set_logger():
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("client.log")
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("logger initialized")


def curses_main(scr, args):
    scr.nodelay(False)
    with Connection(args.host, args.port, "socket.log", "socket.log") as conn:
        logging.info("Connection established")
        command_thread = CommandSenderThread(scr, conn)
        command_thread.start()
        logging.info("Command thread started")
        while command_thread.is_alive():
            try:
                data = conn.read_until(b'\n', timeout=10).decode()
            except nclib.NetcatTimeout:
                logging.info("server is not responding")
            else:
                logging.info("server sent %s", data)
                unpacked_data = json.loads(data)
                raw_map = unpacked_data["raw_map"]
                width = unpacked_data["width"]
                height = unpacked_data["height"]
                field = [raw_map[i * width: (i + 1) * width] for i in range(height)]
                for y in range(height):
                    scr.addstr(y, 0, field[y])
                scr.refresh()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='Server hostname')
    parser.add_argument('--port', type=int, help='Server port', default=DEFAULT_PORT)
    args = parser.parse_args()
    set_logger()
    curses.wrapper(curses_main, args)


if __name__ == '__main__':
    main()
