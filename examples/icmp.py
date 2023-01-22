import socket
from scapy.layers.inet import *
# from scapy.sendrecv import send, sniff, AsyncSniffer

print('Start')
with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
# with socket.socket(socket.AF_PACKET, socket.SOCK_RAW) as sock:
#     sock.bind(('enp0s3', 0x0800))
    # sock.setsockopt(socket.SOL_IP, 1, 0)
    # sock.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
    while True:
        data, addr = sock.recvfrom(65536)
        packet = IP(data)
        # if ICMP not in packet:
        #     continue
        print(f'{addr}: {packet}')
