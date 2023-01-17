import socket
import threading
import time
import sighandler


def producer():
    i = 0
    while True:
        sock.sendto(str.encode('message ' + str(i)), host)
        i = i + 1
        time.sleep(2)


sighandler.register()

host = ('127.0.0.1', 4040)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    t = threading.Thread(target=producer, daemon=True)
    t.start()

    while True:
        data, addr = sock.recvfrom(65536)
        if addr != host:
            print(f'drop packet from {addr}: {data}')
            continue

        print(f'recv {addr}: {data}')
