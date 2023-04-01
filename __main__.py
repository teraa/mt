import logging
import sys
import optparse
from DnsClient import DnsClient
from DnsServer import DnsServer
import config
from BaseClient import *
from TunClient import TunClient
from UdpClient import UdpClient
from UdpServer import UdpServer
from IcmpClient import IcmpClient
from Tunnel import Tunnel
from utils import sighandler


def main():
    sighandler()
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d %(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        level=logging.DEBUG, datefmt='%H:%M:%S')

    parser = optparse.OptionParser()
    parser.add_option('--tif', dest='tif', default=config.TUN_INTERFACE, help='name of the TUN interface to use [%default]')
    parser.add_option('--taddr', dest='taddr', default=config.TUN_ADDRESS, help='TUN address [%default]')
    parser.add_option('--tmask', dest='tmask', default=config.TUN_NETMASK, help='TUN netmask [%default]')
    parser.add_option('--tmtu', dest='tmtu', default=config.TUN_MTU, help='TUN MTU [%default]')

    parser.add_option('--lif', dest='lif', default=config.LISTEN_INTERFACE, help='name of the interface to listen on [%default]')
    parser.add_option('--laddr', dest='laddr', default=config.LISTEN_ADDRESS, help='listen address [%default]')
    parser.add_option('--lport', dest='lport', type='int', default=config.LISTEN_PORT, help='listen port [%default]')

    parser.add_option('--raddr', dest='raddr', default=config.REMOTE_ADDRESS, help='remote address [%default]')
    parser.add_option('--rport', dest='rport', type='int', default=config.REMOTE_PORT, help='remote port [%default]')

    parser.add_option('--mode', dest='mode', default=config.MODE, help='mode (protocol): udpc, udps, dnsc, dnss or icmp [%default]')

    parser.add_option('--domain', dest='domain', default=config.DOMAIN, help='domain to use for DNS tunneling [%default]')
    opt, args = parser.parse_args()

    q = QueuePair((Queue[IP](), Queue[IP]()))

    match opt.mode:
        case 'udpc':
            client1 = UdpClient(q, (opt.raddr, opt.rport))
        case 'dnsc':
            client1 = DnsClient(q, (opt.raddr, opt.rport), opt.domain)
        case 'udps':
            client1 = UdpServer(q, (opt.laddr, opt.lport))
        case 'dnss':
            client1 = DnsServer(q, (opt.laddr, opt.lport), opt.domain)
        case 'icmp':
            client1 = IcmpClient(q, opt.lif, opt.laddr, opt.raddr)
        case _:
            parser.print_help()
            parser.error('Invalid --mode value')
            return 1

    try:
        with TunClient(q, opt.tif, opt.taddr, opt.tmask, opt.tmtu, client1) as client2:
            tunnel = Tunnel(client1, client2)
            tunnel.run()

    finally:
        client1.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
