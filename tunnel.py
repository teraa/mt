import threading
import scapy.layers.inet as inet
from queue import Queue
from clients.base import Base

QueuePair = tuple[Queue[inet.IP], Queue[inet.IP]]

class Tunnel(object):
    def __init__(self, client1: Base, client2: Base):
        self.client1 = client1
        self.client2 = client2

    def run(self):
        threads = []
        targets = [
            (self.client1.reader, f'{type(self.client1).__name__} Reader'),
            (self.client1.writer, f'{type(self.client1).__name__} Writer'),
            (self.client2.reader, f'{type(self.client2).__name__} Reader'),
            (self.client2.writer, f'{type(self.client2).__name__} Writer')
        ]

        for target in targets:
            t = threading.Thread(target=target[0], name=target[1], daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
