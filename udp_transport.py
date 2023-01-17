import logging
import queue
import socket
import errno
from transport import *


class UdpClient(TransportClient):
    def __init__(self, local: tuple[str, int], remote: tuple[str, int]) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(local)
        print(f'Listening on: {local}')

        self._remote = remote
        print(f'Remote host: {remote}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sock.close()

    def reader(self, queue: queue.Queue):
        logging.debug('Start')
        while True:
            try:
                data, addr = self._sock.recvfrom(65535)
                logging.debug(f'{addr} {len(data)} bytes')

                if addr != self._remote:
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
                self._sock.sendto(data, self._remote)
                logging.debug(f'{self._remote} {len(data)} bytes')
                queue.task_done()

            except socket.error as e:
                if e[0] == errno.EINTR:
                    continue
