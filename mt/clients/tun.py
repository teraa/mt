import errno

import pytun
from loguru import logger as logging
from scapy.layers.inet import *

from mt.clients.base import Base
from mt.tunnel import NetworkPipe


class Client(Base):

    def __init__(self, pipe: NetworkPipe, interface: str, address: str, netmask: str, mtu: int):
        super().__init__()
        self._pipe = pipe

        tun = pytun.TunTapDevice(name=interface, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        tun.addr = address
        tun.netmask = netmask
        tun.mtu = mtu
        tun.persist(True)
        tun.up()

        self._tun = tun

    def close(self):
        self._tun.close()

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
        self._pipe.virt.put(packet)

    @tun_guard
    def _write(self):
        packet = self._pipe.wire.get()

        self._tun.write(raw(packet))
        logging.debug(packet)
        self._pipe.wire.task_done()
