import logging
import socket
from BaseClient import *
from utils import socket_guard

Address = tuple[str, int]


class UdpClient(BaseClient):
    def __init__(self, q: QueuePair, serverAddress: Address) -> None:
        super().__init__()
        self._q = q

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # self._sock.bind(local)
        # print(f'Listening on: {local}')

        self._sock.connect(serverAddress)
        print(f'Remote host: {serverAddress}')

    def close(self):
        self._sock.close()

    @socket_guard
    def _read(self):
        data = self._sock.recv(65535)

        try:
            packet: IP = IP(data)
        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return

        self._q[0].put(packet)

    @socket_guard
    def _write(self):
        packet = self._q[1].get()
        data = raw(packet)
        self._sock.sendall(data)
        self._q[1].task_done()
