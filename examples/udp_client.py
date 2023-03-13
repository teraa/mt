import asyncio
import socket
import threading
import time
import utils


async def main():
    utils.sighandler()
    host = ('127.0.0.1', 4040)

    def producer():
        i = 0
        while True:
            message = f'message {i}'
            print(f'send: {message}')
            sock.sendall(str.encode(message))
            i = i + 1
            time.sleep(2)
    
    def consumer():
        while True:
            data = sock.recv(65536)
            print(f'recv: {data}')

    async def producer_async():
        print('Enter')
        await asyncio.sleep(0)
        i = 0
        while True:
            message = f'async message {i}'
            sent = sock.sendto(str.encode(message), host)
            print(f'sent {sent} bytes of: {message}')
            i = i + 1
            await asyncio.sleep(2)

    async def consumer_async():
        await asyncio.sleep(0)
        consumer()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(host)
        t = threading.Thread(target=producer, daemon=True)
        t.start()

        consumer()
        # producer = asyncio.create_task(producer_async())
        # consumer = asyncio.create_task(consumer_async())


        print('bai')

asyncio.run(main())
