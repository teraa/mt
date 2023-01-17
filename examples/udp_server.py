import socket
import sighandler

sighandler.register()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(('0.0.0.0', 4040))
    print('listening')

    while True:
        data, addr = sock.recvfrom(65536)
        print(f'recv {addr}: {data}')
        sock.sendto(str.encode(str.upper(bytes.decode(data))), addr)
