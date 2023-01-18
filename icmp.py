import logging
import socket
import errno
from transport import *
from scapy.layers.inet import *
from scapy.sendrecv import *

Address = str
ICMP_TYPE = 201
ETHERTYPE = 0x0800

# send(IP(dst='f1.lan')/ICMP(type=201)/IP(dst='f1.tun')/ICMP())
class IcmpClient(TransportClient):
    def __init__(self, interface: str, local: Address, remote: Address) -> None:
        super().__init__()

        self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self._sock.bind((interface, ETHERTYPE))
        logging.info(f'Listening on {interface=}')


        self._local = local
        self._remote = remote
        logging.info(f'Remote host: {remote}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sock.close()

    def reader(self):
        logging.debug('Start')
        while True:
            try:
                data, addr = self._sock.recvfrom(65535)
                ether = Ether(data)

                if ICMP not in ether:
                    continue

                ip : IP = ether[IP]
                if ip.src != self._remote:
                    logging.debug(f'Drop packet from {ip.src}')
                    continue
                
                icmp : ICMP = ip[ICMP]
                if icmp.type != ICMP_TYPE:
                    logging.debug(f'Drop ICMP type {icmp.type}')
                    continue

                inner_ip_raw = raw(icmp.payload)
                try:
                    inner_ip : IP = IP(inner_ip_raw)
                except Exception as e:
                    logging.warn(f'Error unpacking ICMP payload: {str(e)}')
                    continue


                logging.debug(inner_ip)
                self.r.put(inner_ip_raw)

            except socket.error as e:
                logging.error(str(e))
                if e.errno == errno.EBADF: # exiting
                    return
                if e.errno == errno.EINTR: # interrupt
                    continue

    def writer(self):
        logging.debug('Start')
        while True:
            try:
                data = self.w.get()
                ip : IP = IP(dst=self._remote)/ICMP(type=ICMP_TYPE)/data
                send(ip, verbose=False)
                logging.debug(IP(data))
                self.w.task_done()

            except socket.error as e:
                logging.error(str(e))
                if e.errno == errno.EBADF: # exiting
                    return
                if e.errno == errno.EINTR: # interrupt
                    continue
