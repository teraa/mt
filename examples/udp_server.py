import socket
import sighandler

sighandler.register()

listen_addr = ('0.0.0.0', 4040)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(listen_addr)
    print(f'Listening on {listen_addr}')

    while True:
        data, addr = sock.recvfrom(65536)
        print(f'recv {addr}: {data}')
        sock.sendto(str.encode(str.upper(bytes.decode(data))), addr)
