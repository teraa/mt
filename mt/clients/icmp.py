import socket

from loguru import logger as logging
from scapy.layers.inet import *

from mt.clients.base import BaseClient
from mt.tunnel import NetworkPipe
from mt.utils import socket_guard

Address = str
ICMP_TYPE = 201
ETHERTYPE = 0x0800

# send(IP(dst='f1.lan')/ICMP(type=201)/IP(dst='f1.tun')/ICMP())


class IcmpClient(BaseClient):
    def __init__(self, pipe: NetworkPipe, interface: str, remote: Address) -> None:
        super().__init__()
        self._pipe = pipe

        self._address = (interface, ETHERTYPE)
        self._remote = remote

        self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self._sock.bind(self._address)

        logging.info(f'Listening on {interface=}')
        logging.info(f'Remote host: {remote}')

    def close(self):
        self._sock.close()

    @socket_guard
    def read(self):
        data, addr = self._sock.recvfrom(65535)
        ether = Ether(data)

        if ICMP not in ether:
            return True

        ip: IP = ether[IP]
        if ip.src != self._remote:
            logging.debug(f'Drop packet from {ip.src}')
            return True

        icmp: ICMP = ip[ICMP]
        if icmp.type != ICMP_TYPE:
            logging.debug(f'Drop ICMP type {icmp.type}')
            return True

        inner_ip_raw = raw(icmp.payload)
        try:
            inner_ip: IP = IP(inner_ip_raw)
        except Exception as e:
            logging.warning(f'Error unpacking ICMP payload: {str(e)}')
            return True

        self._pipe.wire.put(inner_ip)
        return True

    @socket_guard
    def write(self):
        packet = self._pipe.virt.get()
        frame: Ether = Ether()/IP(dst=self._remote)/ICMP(type=ICMP_TYPE)/raw(packet)
        self._sock.sendto(raw(frame), self._address)
        self._pipe.virt.task_done()
        return True
