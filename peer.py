import logging
import queue
import sys
import optparse
import socket
import errno
import threading
import pytun
import config
import sighandler
from udp_transport import *


class TunPeer(object):

    def __init__(self, interface: str, client: TransportClient):
        self._tun = pytun.TunTapDevice(name=interface, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        self._tun.addr = config.TUN_ADDRESS
        self._tun.netmask = config.TUN_NETMASK
        self._tun.mtu = 1500
        self._tun.persist(True)
        self._tun.up()

        self._read_queue = queue.Queue()
        self._write_queue = queue.Queue()

        self._client = client

    def client_reader(self):
        self._client.reader(self._read_queue)

    def client_writer(self):
        self._client.writer(self._write_queue)

    def tun_reader(self):
        logging.debug('Start')
        while True:
            try:
                data = self._tun.read(self._tun.mtu)
                logging.debug(f'{len(data)} bytes')

                self._write_queue.put(data)

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    continue

    def tun_writer(self):
        logging.debug('Start')
        while True:
            try:
                data = self._read_queue.get()
                self._tun.write(data)
                logging.debug(f'{len(data)} bytes')
                self._read_queue.task_done()

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    continue

    def run(self):

        threads = []
        funcs = [
            self.client_reader,
            self.client_writer,
            self.tun_reader,
            self.tun_writer
        ]

        for f in funcs:
            t = threading.Thread(target=f, daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


def main():
    sighandler.register()
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d %(levelname)s] %(funcName)s: %(message)s',
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
