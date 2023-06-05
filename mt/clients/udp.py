import socket

from loguru import logger as logging
from scapy.layers.inet import *

from mt.clients.base import BaseClient
from mt.tunnel import NetworkPipe
from mt.utils import socket_guard

Address = tuple[str, int]


class UdpClient(BaseClient):
    def __init__(self, pipe: NetworkPipe, server_addr: Address) -> None:
        super().__init__()
        self._pipe = pipe

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.connect(server_addr)
        logging.info(f'Remote host: {server_addr}')

    def close(self):
        self._sock.close()

    @socket_guard
    def read(self):
        data = self._sock.recv(65535)

        try:
            packet: IP = IP(data)
        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return True

        self._pipe.wire.put(packet)
        return True

    @socket_guard
    def write(self):
        packet = self._pipe.virt.get()
        data = raw(packet)
        self._sock.sendall(data)
        self._pipe.virt.task_done()
        return True


class UdpServer(BaseClient):
    def __init__(self, pipe: NetworkPipe, listen_addr: Address) -> None:
        super().__init__()
        self._pipe = pipe

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.bind(listen_addr)
        logging.info(f'Listening on: {listen_addr}')

        self._connected = False

    def close(self):
        self._sock.close()

    @socket_guard
    def read(self):
        data, addr = self._sock.recvfrom(65535)

        try:
            packet: IP = IP(data)

            if not self._connected:
                self._sock.connect(addr)
                logging.info(f'Client connected: {addr}')
                self._connected = True

        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return True

        self._pipe.wire.put(packet)
        return True

    @socket_guard
    def write(self):
        packet = self._pipe.virt.get()

        if not self._connected:
            logging.warn(f'Dropping packed because not connected')
            return True

        data = raw(packet)
        self._sock.sendall(data)
        self._pipe.virt.task_done()
        return True
