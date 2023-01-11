import socket
import pytun
import fcntl

host = '10.0.1.170'
port = 5000
tun = pytun.TunTapDevice('mt')

print(repr(tun))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    print(f'Connected to {host}:{port}')
    while True:
        data = s.recv(1024)
        if not data:
            print('Host disconnected')
            break
        print('Received:', data)
