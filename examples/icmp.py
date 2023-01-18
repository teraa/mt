import socket
from scapy.layers.inet import *
# from scapy.sendrecv import send, sniff, AsyncSniffer

print('Start')
with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
    # sock.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
    while True:
        data, addr = sock.recvfrom(65536)
        packet = IP(data)
        print(f'{addr}: {packet}')
