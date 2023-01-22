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

    def close(self):
        self._sock.close()

    def reader(self):
        logging.debug('Start')
        while True:
            try:
                data, addr = self._sock.recvfrom(65535)

                if addr != self._remote:
                    logging.debug(f'Drop packet from {addr}')
                    continue

                try:
                    packet: IP = IP(data)
                except Exception as e:
                    logging.warn(f'Error unpacking payload: {str(e)}')
                    continue

                self.r.put(packet)

            except socket.error as e:
                logging.error(str(e))
                if e.errno == errno.EBADF:  # exiting
                    return
                if e.errno == errno.EINTR:  # interrupt
                    continue

    def writer(self):
        logging.debug('Start')
        while True:
            try:
                packet = self.w.get()
                data = raw(packet)
                self._sock.sendto(data, self._remote)
                self.w.task_done()

            except socket.error as e:
                logging.error(str(e))
                if e.errno == errno.EBADF:  # exiting
                    return
                if e.errno == errno.EINTR:  # interrupt
                    continue
