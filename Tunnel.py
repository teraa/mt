import threading
from BaseClient import BaseClient


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

        for target in targets:
            t = threading.Thread(target=target[0], name=target[1], daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()