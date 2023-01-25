import logging
import socket
from transport import *

Address = tuple[str, int]


class UdpClient(TransportClient):
    def __init__(self, local: Address, remote: Address) -> None:
        super().__init__()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.bind(local)
        print(f'Listening on: {local}')

        self._sock.connect(remote)
        print(f'Remote host: {remote}')

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

        self.r.put(packet)

    @socket_guard
    def _write(self):
        packet = self.w.get()
        data = raw(packet)
        self._sock.sendall(data)
        self.w.task_done()
