import logging
import errno
import threading
import pytun
from transport import *


class TunPeer(object):

    def __init__(self, interface: str, address: str, netmask: str, mtu: int, client: TransportClient):
        tun = pytun.TunTapDevice(name=interface, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        tun.addr = address
        tun.netmask = netmask
        tun.mtu = mtu
        tun.persist(True)
        tun.up()

        self._tun = tun
        self._client = client

    def reader(self):
        logging.debug('Start')
        while True:
            try:
                data = self._tun.read(self._tun.mtu)
                packet = IP(data)

                if packet.proto == 2:
                    logging.debug('Drop igmp')
                    continue

                if packet.proto == 128:
                    logging.debug('Drop sscopmce')
                    continue

                if TCP in packet and packet[TCP].dport == 5355:
                    logging.debug('Drop hostmon')
                    continue

                logging.debug(packet)
                self._client.w.put(packet)

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    continue

    def writer(self):
        logging.debug('Start')
        while True:
            try:
                packet = self._client.r.get()

                self._tun.write(raw(packet))
                logging.debug(packet)
                self._client.r.task_done()

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    continue

    def run(self):

        threads = []
        targets = [
            (self._client.reader, 'Client Reader'),
            (self._client.writer, 'Client Writer'),
            (self.reader, 'TUN Reader'),
            (self.writer, 'TUN Writer')
        ]

        for target in targets:
            t = threading.Thread(target=target[0], name=target[1], daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()