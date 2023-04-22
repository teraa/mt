import logging
import socket
from scapy.layers.dns import *
from tunnel import QueuePair
from utils import socket_guard
from .base import Base

Address = tuple[str, int]


class Client(Base):
    def __init__(self, q: QueuePair, server_addr: Address, domain: str) -> None:
        super().__init__()
        self._q = q

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.connect(server_addr)
        logging.info(f'Remote host: {server_addr}')

        self._domain = domain

    def close(self):
        self._sock.close()

    @socket_guard
    def _read(self):
        data = self._sock.recv(65535)

        try:
            dns: DNS = DNS(data)
            rdata: bytes = dns.ar.rdata
            packet: IP = IP(rdata)

        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return

        self._q[0].put(packet)

    @socket_guard
    def _write(self):
        packet = self._q[1].get()

        qd = DNSQR(qname=self._domain, qtype='A')
        ar = DNSRR(type='NULL', rdata=packet)
        dns = DNS(qr=0, qd=qd, ar=ar, arcount=1)

        data = raw(dns)
        self._sock.sendall(data)
        self._q[1].task_done()


class Server(Base):
    def __init__(self, q: QueuePair, listen_addr: Address, domain: str) -> None:
        super().__init__()
        self._q = q

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.bind(listen_addr)
        logging.info(f'Listening on: {listen_addr}')

        self._domain = domain

        self._connected = False

    def close(self):
        self._sock.close()

    @socket_guard
    def _read(self):
        data, addr = self._sock.recvfrom(65535)

        try:
            dns: DNS = DNS(data)
            rdata: bytes = dns.ar.rdata
            packet: IP = IP(rdata)

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

        qd = DNSQR(qname=self._domain, qtype='A')
        an = DNSRR(rrname=qd.name, type=qd.qtype, rdata='0.0.0.0')
        ar = DNSRR(type='NULL', rdata=packet)
        dns = DNS(qr=1, qd=qd, an=an, ar=ar, arcount=1)

        data = raw(dns)
        self._sock.sendall(data)
        self._q[1].task_done()
