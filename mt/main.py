import signal
import threading

from mt.clients import dns, icmp, tun, udp
from mt.parser import create_parser
from mt.tunnel import NetworkPipe, Tunnel
from mt.utils import excepthook, sighandler


def main():
    signal.signal(signal.SIGINT, sighandler)
    threading.excepthook = excepthook

    parser = create_parser()
    args = parser.parse_args()

    pipe = NetworkPipe()

    match args.mode:
        case 'udpc':
            client1 = udp.Client(pipe, (args.addr, args.port))
        case 'udps':
            client1 = udp.Server(pipe, (args.addr, args.port))
        case 'dnsc':
            client1 = dns.Client(pipe, (args.addr, args.port), args.domain, args.keepalive)
        case 'dnss':
            client1 = dns.Server(pipe, (args.addr, args.port), args.domain)
        case 'icmp':
            client1 = icmp.Client(pipe, args.lif, args.addr)

    try:
        with tun.Client(pipe, args.tif, args.taddr, args.tmask, args.tmtu) as client2:
            tunnel = Tunnel(client1, client2)
            tunnel.run()

    finally:
        client1.close()

    return 0
