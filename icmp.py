import logging
import socket
from transport import *

Address = str
ICMP_TYPE = 201
ETHERTYPE = 0x0800

# send(IP(dst='f1.lan')/ICMP(type=201)/IP(dst='f1.tun')/ICMP())


class IcmpClient(TransportClient):
    def __init__(self, interface: str, local: Address, remote: Address) -> None:
        super().__init__()

        self._address = (interface, ETHERTYPE)
        self._local = local
        self._remote = remote

        self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self._sock.bind(self._address)

        logging.info(f'Listening on {interface=}')
        logging.info(f'Remote host: {remote}')

    def close(self):
        self._sock.close()

    @TransportClient.socket_catch
    def read(self):
        data, addr = self._sock.recvfrom(65535)
        ether = Ether(data)

        if ICMP not in ether:
            return

        ip: IP = ether[IP]
        if ip.src != self._remote:
            logging.debug(f'Drop packet from {ip.src}')
            return

        icmp: ICMP = ip[ICMP]
        if icmp.type != ICMP_TYPE:
            logging.debug(f'Drop ICMP type {icmp.type}')
            return

        inner_ip_raw = raw(icmp.payload)
        try:
            inner_ip: IP = IP(inner_ip_raw)
        except Exception as e:
            logging.warn(f'Error unpacking ICMP payload: {str(e)}')
            return

        self.r.put(inner_ip)

    @TransportClient.socket_catch
    def write(self):
        packet = self.w.get()
        frame: Ether = Ether()/IP(dst=self._remote)/ICMP(type=ICMP_TYPE)/raw(packet)
        self._sock.sendto(raw(frame), self._address)
        self.w.task_done()
