#! /usr/bin/env python3

import argparse
import curses
import json
import logging
import threading
from socket import timeout

from sockwrapper import SocketWrapper, ClientConnection


key_to_direction = {
    'w': 'up',
    'a': 'left',
    's': 'down',
    'd': 'right',
}

WIDTH = 51
HEIGHT = 51
DEFAULT_PORT = 1488


class CommandSenderThread(threading.Thread):
    def __init__(self, scr, conn: SocketWrapper):
        super(CommandSenderThread, self).__init__()
        self._scr = scr
        self._conn = conn

    def run(self):
        try:
            while True:
                key = self._scr.getch()
                curses.flushinp()
                if key == ord('q'):
                    return
                direction = key_to_direction.get(chr(key), None)
                if direction is not None:
                    self._conn.send_line(json.dumps({"direction": direction}).encode(), end=b'\n')
        except Exception:
            logging.exception("Exception occured in CommandSenderThread")
            return  # Stop thread after any error


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
    command_thread = None
    try:
        with ClientConnection(args.host, args.port, args.ipv6, timeout=1.0) as conn:
            logging.info("Connection established")
            command_thread = CommandSenderThread(scr, conn)
            command_thread.start()
            logging.info("Command thread started")
            while command_thread.is_alive():
                try:
                    data = conn.recv_until(b'\n').decode()
                except timeout:
                    logging.info("server is not responding")
                else:
                    logging.info("server sent %s", data)
                    unpacked_data = json.loads(data)
                    type = unpacked_data["type"]
                    if type == "tick":
                        raw_map = unpacked_data["raw_map"]
                        width = unpacked_data["width"]
                        height = unpacked_data["height"]
                        field = [raw_map[i * width: (i + 1) * width] for i in range(height)]
                        for y in range(height):
                            scr.addstr(y, 0, field[y])
                    elif type == "end_game":
                        scr.clear()
                        scr.addstr(0, 0, "GAME OVER")
                    scr.refresh()

    except Exception:
        if command_thread:
            command_thread.join()
        logging.exception("Exception occured in curses_main")
        return  # Quit from curses win properly


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='Server hostname')
    parser.add_argument('--port', type=int, help='Server port', default=DEFAULT_PORT)
    parser.add_argument("--ipv6", help="Use ipv6", action="store_true")
    args = parser.parse_args()
    set_logger()
    curses.wrapper(curses_main, args)
    exit(0)


if __name__ == '__main__':
    main()
