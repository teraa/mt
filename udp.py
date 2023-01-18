import logging
import socket
import errno
from transport import *

Address = tuple[str, int]

class UdpClient(TransportClient):
    def __init__(self, local: Address, remote: Address) -> None:
        super().__init__()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(local)
        print(f'Listening on: {local}')

        self._remote = remote
        print(f'Remote host: {remote}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        self._sock.close()

    def reader(self):
        logging.debug('Start')
        while True:
            try:
                data, addr = self._sock.recvfrom(65535)
                logging.debug(f'{addr} {len(data)} bytes')

                if addr != self._remote:
                    logging.debug(f'Drop packet from {addr}')
                    continue

                self.r.put(data)

            except socket.error as e:
                if e[0] == errno.EINTR:
                    continue

    def writer(self):
        logging.debug('Start')
        while True:
            try:
                data = self.w.get()
                self._sock.sendto(data, self._remote)
                logging.debug(f'{self._remote} {len(data)} bytes')
                self.w.task_done()

            except socket.error as e:
                if e[0] == errno.EINTR:
                    continue
