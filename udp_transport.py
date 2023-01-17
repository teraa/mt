import logging
import queue
import socket
import errno
from transport import *


class UdpClient(TransportClient):
    def __init__(self, laddr: str, lport: int, raddr: str, rport: int) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((laddr, lport))
        print(f'Listening on: {laddr}:{lport}')

        self._raddr = raddr
        self._rport = rport
        print(f'Remote host: {raddr}:{rport}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sock.close()

    def reader(self, queue: queue.Queue):
        logging.debug('Start')
        while True:
            try:
                data, addr = self._sock.recvfrom(65535)
                logging.debug(f'{len(data)} bytes')

                if addr[0] != self._raddr or addr[1] != self._rport:
                    logging.debug(f'Drop packet from {addr}')
                    continue

                queue.put(data)

            except socket.error as e:
                if e[0] == errno.EINTR:
                    continue

    def writer(self, queue: queue.Queue):
        logging.debug('Start')
        while True:
            try:
                data = queue.get()
                self._sock.sendto(data, (self._raddr, self._rport))
                logging.debug(f'{len(data)} bytes')
                queue.task_done()

            except socket.error as e:
                if e[0] == errno.EINTR:
                    continue
