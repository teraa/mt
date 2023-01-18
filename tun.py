import logging
import sys
import optparse
import errno
import threading
import pytun
import config
import sighandler
from udp import *


class TunPeer(object):

    def __init__(self, interface: str, client: TransportClient):
        tun = pytun.TunTapDevice(name=interface, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        tun.addr = config.TUN_ADDRESS
        tun.netmask = config.TUN_NETMASK
        tun.mtu = 400
        tun.persist(True)
        tun.up()
        
        self._tun = tun
        self._client = client

    def reader(self):
        logging.debug('Start')
        while True:
            try:
                data = self._tun.read(self._tun.mtu)
                logging.debug(f'{len(data)} bytes')

                self._client.w.put(data)

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    continue

    def writer(self):
        logging.debug('Start')
        while True:
            try:
                data = self._client.r.get()
                self._tun.write(data)
                logging.debug(f'{len(data)} bytes')
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
    parser.add_option('-i', dest='interface', default=config.INTERFACE, help='TUN interface to use [%default]')
    parser.add_option('-a', dest='laddr', default='0.0.0.0', help='local address [%default]')
    parser.add_option('-p', dest='lport', type='int', default=config.LOCAL_PORT, help='local port [%default]')
    parser.add_option('-A', dest='raddr', default=config.REMOTE_ADDRESS, help='remote address [%default]')
    parser.add_option('-P', dest='rport', type='int', default=config.REMOTE_PORT, help='remote port [%default]')
    opt, args = parser.parse_args()

    if not opt.raddr:
        parser.print_help()
        return 1

    with UdpClient((opt.laddr, opt.lport), (opt.raddr, opt.rport)) as client:
        peer = TunPeer(opt.interface, client)
        peer.run()

    return 0


if __name__ == '__main__':
    sys.exit(main())
