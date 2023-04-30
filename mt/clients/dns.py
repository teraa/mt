import socket
from queue import Empty

from loguru import logger as logging
from scapy.layers.dns import *

from mt.clients.base import Base
from mt.tunnel import NetworkPipe
from mt.utils import socket_guard

Address = tuple[str, int]


class Client(Base):
    def __init__(self, pipe: NetworkPipe, server_addr: Address, domain: str, keepalive: float) -> None:
        super().__init__()
        self._pipe = pipe

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.connect(server_addr)
        logging.info(f'Remote host: {server_addr}')

        self._domain = domain
        self._keepalive = keepalive or None

    def close(self):
        self._sock.close()

    @socket_guard
    def read(self):
        data = self._sock.recv(65535)

        try:
            dns: DNS = DNS(data)

            if not dns.ar:
                logging.debug('Pong')
                return True

            rdata: bytes = dns.ar.rdata
            packet: IP = IP(rdata)

        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')
            return True

        self._pipe.wire.put(packet)
        return True

    @socket_guard
    def write(self):

        qd = DNSQR(qname=self._domain, qtype='A')
        timeout = False

        try:
            packet = self._pipe.virt.get(timeout=self._keepalive)
            ar = DNSRR(type='NULL', rdata=packet)
            dns = DNS(qr=0, qd=qd, ar=ar, arcount=1)
        except Empty:
            timeout = True
            logging.debug('Ping')
            dns = DNS(qr=0, qd=qd)

        data = raw(dns)
        self._sock.sendall(data)

        if not timeout:
            self._pipe.virt.task_done()

        return True


class Server(Base):
    def __init__(self, pipe: NetworkPipe, listen_addr: Address, domain: str) -> None:
        super().__init__()
        self._pipe = pipe

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.bind(listen_addr)
        logging.info(f'Listening on: {listen_addr}')

        self._domain = domain

        self._connected = False

    def close(self):
        self._sock.close()

    @socket_guard
    def read(self):
        data, addr = self._sock.recvfrom(65535)

        try:
            dns: DNS = DNS(data)
            packet: IP | None

            if dns.ar:
                rdata: bytes = dns.ar.rdata
                packet = IP(rdata)
            else:
                packet = None

            if not self._connected:
                self._sock.connect(addr)
                logging.info(f'Client connected: {addr}')
                self._connected = True
            
            if packet:
                self._pipe.wire.put(packet)
            else:
                logging.debug('Ping')
                self._pipe.virt.put(None)


        except Exception as e:
            logging.warn(f'Error unpacking payload: {str(e)}')

        return True

    @socket_guard
    def write(self):
        packet = self._pipe.virt.get()

        if not self._connected:
            logging.warn(f'Dropping packed because not connected')
            return True

        qd = DNSQR(qname=self._domain, qtype='A')

        if packet:
            an = DNSRR(rrname=qd.name, type=qd.qtype, rdata='0.0.0.0')
            ar = DNSRR(type='NULL', rdata=packet)
            dns = DNS(qr=1, qd=qd, an=an, ar=ar, arcount=1)
        else:
            logging.debug('Pong')
            dns = DNS(qr=1, qd=qd, rcode=3)

        data = raw(dns)
        self._sock.sendall(data)
        self._pipe.virt.task_done()
        return True
