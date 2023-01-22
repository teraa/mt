import logging
import sys
import optparse
import errno
import threading
import pytun
import config
import sighandler
from transport import TransportClient
from udp import UdpClient
from icmp import IcmpClient
from scapy.layers.inet import *


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


def main():
    sighandler.register()
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d %(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        level=logging.DEBUG, datefmt='%H:%M:%S')

    parser = optparse.OptionParser()
    parser.add_option('--tif', dest='tif', default=config.TUN_INTERFACE, help='name of the TUN interface to use [%default]')
    parser.add_option('--taddr', dest='taddr', default=config.TUN_ADDRESS, help='TUN address [%default]')
    parser.add_option('--tmask', dest='tmask', default=config.TUN_NETMASK, help='TUN netmask [%default]')
    parser.add_option('--tmtu', dest='tmtu', default=config.TUN_MTU, help='TUN MTU [%default]')

    parser.add_option('--lif', dest='lif', default=config.LOCAL_INTERFACE, help='name of the local interface to use [%default]')
    parser.add_option('--laddr', dest='laddr', default='0.0.0.0', help='local address [%default]')
    parser.add_option('--lport', dest='lport', type='int', default=config.LOCAL_PORT, help='local port [%default]')

    parser.add_option('--raddr', dest='raddr', default=config.REMOTE_ADDRESS, help='remote address [%default]')
    parser.add_option('--rport', dest='rport', type='int', default=config.REMOTE_PORT, help='remote port [%default]')

    parser.add_option('--proto', dest='proto', default='icmp', help='protocol to use: udp or icmp [%default]')
    opt, args = parser.parse_args()

    match opt.proto:
        case 'udp':
            client = UdpClient((opt.laddr, opt.lport), (opt.raddr, opt.rport))
        case 'icmp':
            client = IcmpClient(opt.lif, opt.laddr, opt.raddr)
        case _:
            parser.print_help()
            parser.error('Invalid --proto value')
            return 1
    
    try:
        peer = TunPeer(opt.tif, opt.taddr, opt.tmask, opt.tmtu, client)
        peer.run()
    finally:
        client.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
