import logging
import errno
import threading
import pytun
from baseclient import *


class TunPeer(BaseClient):

    def __init__(self, interface: str, address: str, netmask: str, mtu: int, client: BaseClient):
        tun = pytun.TunTapDevice(name=interface, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        tun.addr = address
        tun.netmask = netmask
        tun.mtu = mtu
        tun.persist(True)
        tun.up()

        self._tun = tun
        self._client = client

    def tun_guard(func):
        def tun_guard(*args):
            try:
                func(*args)
                return True

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    return True

                logging.exception(e)
                raise

        return tun_guard

    @tun_guard
    def _read(self):
        data = self._tun.read(self._tun.mtu)
        packet = IP(data)

        if packet.proto == 2:
            logging.debug('Drop igmp')
            return

        if packet.proto == 128:
            logging.debug('Drop sscopmce')
            return

        if TCP in packet and packet[TCP].dport == 5355:
            logging.debug('Drop hostmon')
            return

        logging.debug(packet)
        self._client.w.put(packet)

    @tun_guard
    def _write(self):
        packet = self._client.r.get()

        self._tun.write(raw(packet))
        logging.debug(packet)
        self._client.r.task_done()

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
