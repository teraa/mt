import threading
from queue import Queue

from scapy.layers.inet import IP

from mt.clients.base import BaseClient


class NetworkPipe(object):
    def __init__(self) -> None:
        self.virt = Queue[IP | None]()
        self.wire = Queue[IP]()

class Tunnel(object):
    def __init__(self, client1: BaseClient, client2: BaseClient):
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

        threads = [threading.Thread(target=target[0], name=target[1], daemon=True) for target in targets]

        for thread in threads:
            thread.start()

        for t in threads:
            t.join()
