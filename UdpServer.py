import logging
import socket
from BaseClient import *
from utils import socket_guard

Address = tuple[str, int]


class UdpServer(BaseClient):
    def __init__(self, q: QueuePair, listenAddress: Address) -> None:
        super().__init__()
        self._q = q

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.bind(listenAddress)
        logging.info(f'Listening on: {listenAddress}')

        self._connected = False

    def close(self):
        self._sock.close()

    @socket_guard
    def _read(self):
        data, addr = self._sock.recvfrom(65535)

        try:
            packet: IP = IP(data)

            if not self._connected:
                self._sock.connect(addr)
                logging.info(f'Client connected: {addr}')
                self._connected = True

        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return

        self._q[0].put(packet)

    @socket_guard
    def _write(self):
        packet = self._q[1].get()

        if not self._connected:
            logging.warn(f'Dropping packed because not connected')
            return

        data = raw(packet)
        self._sock.sendall(data)
        self._q[1].task_done()
