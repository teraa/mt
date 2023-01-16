import queue
import sys
import optparse
import socket
import select
import errno
import threading
import pytun
import config
import sighandler

debug_lock = threading.Lock()


def debug(message):
    debug_lock.acquire()
    print(message, file=sys.stderr)
    debug_lock.release()


class TunPeer(object):

    def __init__(self, interface, laddr, lport, raddr, rport):
        self._tun = pytun.TunTapDevice(name=interface, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        self._tun.addr = config.TUN_ADDRESS
        self._tun.netmask = config.TUN_NETMASK
        self._tun.mtu = 1500
        self._tun.persist(True)
        self._tun.up()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((laddr, lport))
        print(f'Listening on: {laddr}:{lport}')

        self._raddr = raddr
        self._rport = rport
        print(f'Remote host: {raddr}:{rport}')

        self._read_queue = queue.Queue()
        self._write_queue = queue.Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sock.close()

    def socket_reader(self):
        debug('SR')
        while True:
            try:
                data, addr = self._sock.recvfrom(65535)
                debug(f'SR: {len(data)} bytes')

                if addr[0] != self._raddr or addr[1] != self._rport:
                    debug(f'Drop packet from {addr}')
                    continue

                self._read_queue.put(data)

            except socket.error as e:
                if e[0] == errno.EINTR:
                    continue

    def socket_writer(self):
        debug('SW')
        while True:
            try:
                data = self._write_queue.get()
                self._sock.sendto(data, (self._raddr, self._rport))
                debug(f'SW: {len(data)} bytes')
                self._write_queue.task_done()

            except socket.error as e:
                if e[0] == errno.EINTR:
                    continue

    def tun_reader(self):
        debug('TR')
        while True:
            try:
                data = self._tun.read(self._tun.mtu)
                debug(f'TR: {len(data)} bytes')

                self._write_queue.put(data)

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    continue

    def tun_writer(self):
        debug('TW')
        while True:
            try:
                data = self._read_queue.get()
                self._tun.write(data)
                debug(f'TW: {len(data)} bytes')
                self._read_queue.task_done()

            except pytun.Error as e:
                if e[0] == errno.EINTR:
                    continue

    def run(self):

        threads = []
        funcs = [
            self.socket_reader,
            self.socket_writer,
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

    with TunPeer(opt.interface, opt.laddr, opt.lport, opt.raddr, opt.rport) as peer:
        peer.run()

    return 0


if __name__ == '__main__':
    sys.exit(main())
