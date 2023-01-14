import signal
import sys
import optparse
import socket
import select
import errno
import pytun
import config


class TunPeer(object):

    def __init__(self, interface, laddr, lport, raddr, rport):
        self._tun = pytun.TunTapDevice(name=interface, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((laddr, lport))
        print(f'Listening on: {laddr}:{lport}')

        self._raddr = raddr
        self._rport = rport
        print(f'Remote host: {raddr}:{rport}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sock.close()

    def run(self):
        r = [self._tun, self._sock]
        w = []
        x = []
        tq = ''
        sq = ''

        while True:
            try:
                r, w, x = select.select(r, w, x)

                if self._tun in r:
                    sq = self._tun.read(self._tun.mtu)
                    print(f'TR: {len(sq)} bytes', file=sys.stderr)

                if self._sock in r:
                    tq, addr = self._sock.recvfrom(65535)
                    print(f'SR: {len(tq)} bytes', file=sys.stderr)
                    if addr[0] != self._raddr or addr[1] != self._rport:
                        tq = ''  # drop packet
                        print(f'Drop packet from {addr}', file=sys.stderr)

                if self._tun in w:
                    self._tun.write(tq)
                    print(f'TW: {len(tq)} bytes', file=sys.stderr)
                    tq = ''

                if self._sock in w:
                    self._sock.sendto(sq, (self._raddr, self._rport))
                    print(f'SW: {len(sq)} bytes', file=sys.stderr)
                    sq = ''

                r = []
                w = []

                if tq:
                    w.append(self._tun)
                else:
                    r.append(self._sock)

                if sq:
                    w.append(self._sock)
                else:
                    r.append(self._tun)

            except (select.error, socket.error, pytun.Error) as e:
                if e[0] == errno.EINTR:
                    continue
                print(str(e), file=sys.stderr)
                break


def main():
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
        peer.run();

    return 0

def sigint_handler(sig_num, frame):
    print('\nExiting...')
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
    sys.exit(main())
