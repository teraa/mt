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

        self._remote = remote
        print(f'Remote host: {remote}')

    def close(self):
        self._sock.close()

    @TransportClient.socket_catch
    def read(self):
        data, addr = self._sock.recvfrom(65535)

        if addr != self._remote:
            logging.debug(f'Drop packet from {addr}')
            return

        try:
            packet: IP = IP(data)
        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return

        self.r.put(packet)

    @TransportClient.socket_catch
    def write(self):
        packet = self.w.get()
        data = raw(packet)
        self._sock.sendto(data, self._remote)
        self.w.task_done()
        raise socket.error()
