import logging
import socket
from scapy.layers.inet import *
from mt.tunnel import QueuePair
from mt.utils import socket_guard
from mt.clients.base import Base


Address = tuple[str, int]


class Client(Base):
    def __init__(self, q: QueuePair, server_addr: Address) -> None:
        super().__init__()
        self._q = q

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.connect(server_addr)
        logging.info(f'Remote host: {server_addr}')

    def close(self):
        self._sock.close()

    @socket_guard
    def _read(self):
        data = self._sock.recv(65535)

        try:
            packet: IP = IP(data)
        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return True

        self._q[0].put(packet)
        return True

    @socket_guard
    def _write(self):
        packet = self._q[1].get()
        data = raw(packet)
        self._sock.sendall(data)
        self._q[1].task_done()
        return True


class Server(Base):
    def __init__(self, q: QueuePair, listen_addr: Address) -> None:
        super().__init__()
        self._q = q

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.bind(listen_addr)
        logging.info(f'Listening on: {listen_addr}')

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
            return True

        self._q[0].put(packet)
        return True

    @socket_guard
    def _write(self):
        packet = self._q[1].get()

        if not self._connected:
            logging.warn(f'Dropping packed because not connected')
            return True

        data = raw(packet)
        self._sock.sendall(data)
        self._q[1].task_done()
        return True
