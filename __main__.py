import logging
import sys
import optparse
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

    parser.add_option('--lif', dest='lif', default=config.LOCAL_INTERFACE, help='name of the local interface to use [%default]')
    parser.add_option('--laddr', dest='laddr', default='0.0.0.0', help='local address [%default]')
    parser.add_option('--lport', dest='lport', type='int', default=config.LOCAL_PORT, help='local port [%default]')

    parser.add_option('--raddr', dest='raddr', default=config.REMOTE_ADDRESS, help='remote address [%default]')
    parser.add_option('--rport', dest='rport', type='int', default=config.REMOTE_PORT, help='remote port [%default]')

    parser.add_option('--proto', dest='proto', default='udpc', help='protocol to use: udp or icmp [%default]')
    opt, args = parser.parse_args()

    q = QueuePair((Queue[IP](), Queue[IP]()))

    match opt.proto:
        case 'udpc':
            client1 = UdpClient(q, (opt.raddr, opt.rport))
        case 'udps':
            client1 = UdpServer(q, (opt.laddr, opt.lport))
        case 'icmp':
            client1 = IcmpClient(q, opt.lif, opt.laddr, opt.raddr)
        case _:
            parser.print_help()
            parser.error('Invalid --proto value')
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
