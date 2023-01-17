import queue

class TransportClient():
    def __init__(self) -> None:
        self.r = queue.Queue()
        self.w = queue.Queue()

    def reader(self):
        pass

    def writer(self):
        pass