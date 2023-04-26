import scapy.layers.inet as inet
import logging
from mt.parser import create_parser
from mt.clients import dns, icmp, tun, udp
from mt.tunnel import NetworkPipe, Tunnel
from mt.utils import sighandler


def main():
    sighandler()
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d %(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        level=logging.DEBUG, datefmt='%H:%M:%S')

    parser = create_parser()
    args = parser.parse_args()

    q = NetworkPipe()

    match args.mode:
        case 'udpc':
            client1 = udp.Client(q, (args.addr, args.port))
        case 'udps':
            client1 = udp.Server(q, (args.addr, args.port))
        case 'dnsc':
            client1 = dns.Client(q, (args.addr, args.port), args.domain, args.keepalive)
        case 'dnss':
            client1 = dns.Server(q, (args.addr, args.port), args.domain)
        case 'icmp':
            client1 = icmp.Client(q, args.lif, args.addr)

    try:
        with tun.Client(q, args.tif, args.taddr, args.tmask, args.tmtu) as client2:
            tunnel = Tunnel(client1, client2)
            tunnel.run()

    finally:
        client1.close()

    return 0
