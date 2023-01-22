from scapy.layers.inet import *
from queue import Queue


class TransportClient():
    def __init__(self) -> None:
        self.r = Queue[IP]()
        self.w = Queue[IP]()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        raise NotImplementedError()

    def reader(self):
        raise NotImplementedError()

    def writer(self):
        raise NotImplementedError()
