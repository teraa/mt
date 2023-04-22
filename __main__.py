import argparse
import logging
import sys
from scapy.layers.inet import *
from queue import Queue
from Clients import Dns, Icmp, Tun, Udp
from Clients import QueuePair
from Tunnel import Tunnel
from utils import sighandler


def main():
    sighandler()
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d %(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        level=logging.DEBUG, datefmt='%H:%M:%S')

    parser = argparse.ArgumentParser()
    parser.add_argument('--tif', default='mt', help='TUN interface name [%(default)s]', metavar='NAME')
    parser.add_argument('--taddr', default='10.20.0.1', help='TUN address [%(default)s]')
    parser.add_argument('--tmask', default='255.255.255.0', help='TUN netmask [%(default)s]')
    parser.add_argument('--tmtu', default=1472, type=int, help='TUN MTU [%(default)s]')

    subparsers = parser.add_subparsers(title='modes', dest='mode', required=True)

    server_parser = argparse.ArgumentParser(add_help=False)
    server_parser.add_argument('--addr', default='0.0.0.0', help='listen address [%(default)s]')
    server_parser.add_argument('--port', default=50142, type=int, help='listen port [%(default)s]')

    client_parser = argparse.ArgumentParser(add_help=False)
    client_parser.add_argument('--addr', default='192.168.56.106', help='remote address [%(default)s]')
    client_parser.add_argument('--port', default=50142, type=int, help='remote port [%(default)s]')

    dns_parser = argparse.ArgumentParser(add_help=False)
    dns_parser.add_argument('--domain', default='example.org', help='domain to use for DNS tunneling [%(default)s]')

    udpc_parser = subparsers.add_parser('udpc', help='UDP client', parents=[client_parser])

    udps_parser = subparsers.add_parser('udps', help='UDP server', parents=[server_parser])

    dnsc_parser = subparsers.add_parser('dnsc', help='DNS client', parents=[client_parser, dns_parser])

    dnss_parser = subparsers.add_parser('dnss', help='DNS server', parents=[server_parser, dns_parser])

    icmp_parser = subparsers.add_parser('icmp', help='ICMP client')
    icmp_parser.add_argument('--lif', default='enp0s8', help='listen interface [%(default)s]')
    icmp_parser.add_argument('--raddr', default='192.168.56.106', help='remote address [%(default)s]')
    icmp_parser.add_argument('--laddr', default='192.168.56.105', help='local address [%(default)s]')
    
    args = parser.parse_args()

    q = QueuePair((Queue[IP](), Queue[IP]()))

    match args.mode:
        case 'udpc':
            client1 = Udp.Client(q, (args.addr, args.port))
        case 'udps':
            client1 = Udp.Server(q, (args.addr, args.port))
        case 'dnsc':
            client1 = Dns.Client(q, (args.addr, args.port), args.domain)
        case 'dnss':
            client1 = Dns.Server(q, (args.addr, args.port), args.domain)
        case 'icmp':
            client1 = Icmp.Client(q, args.lif, args.laddr, args.raddr)

    try:
        with Tun.Client(q, args.tif, args.taddr, args.tmask, args.tmtu, client1) as client2:
            tunnel = Tunnel(client1, client2)
            tunnel.run()

    finally:
        client1.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
