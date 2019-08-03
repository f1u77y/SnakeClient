#! /usr/bin/env python3

import argparse
import curses
import threading

import nclib.netcat


key_to_direction = {
    'w': 'up',
    'a': 'left',
    's': 'down',
    'd': 'right',
}


class CommandSenderThread(threading.Thread):
    def __init__(self, scr, conn):
        super().__init__()
        self._scr = scr
        self._conn = conn

    def run(self):
        while True:
            key = self._scr.getkey()
            if key == ord('q'):
                sys.exit(0)
            direction = key_to_direction.get(chr(key), None)
            if direction is not None:
                self._conn.send_line(direction.encode('ascii'), ending=b'\n')


WIDTH = 51
HEIGHT = 51


def curses_main(scr):
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='Server hostname')
    parser.add_argument('port', type=int, help='Server port')
    args = parser.parse_args()

    conn = nclib.netcat.Netcat(connect=(args.host, args.port))
    command_sender = CommandSenderThread(scr, conn)
    command_sender.start()

    while True:
        field_str = conn.read_until(b'\n')
        field = [[None for x in range(WIDTH)] for y in range(HEIGHT)]
        for x in range(WIDTH):
            for y in range(HEIGHT):
                field[y][x] = field_str[x * HEIGHT + y]
        for y in range(HEIGHT):
            field[y] = ''.join(field[y])
            scr.addstr(y, 0, field[y])


def main():
    curses.wrapper(curses_main)


if __name__ == '__main__':
    main()
