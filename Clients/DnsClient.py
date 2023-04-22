import logging
import socket
from scapy.layers.dns import *
from .BaseClient import *
from utils import socket_guard

Address = tuple[str, int]


class DnsClient(BaseClient):
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
