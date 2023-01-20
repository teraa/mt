import queue


class TransportClient():
    def __init__(self) -> None:
        self.r = queue.Queue()
        self.w = queue.Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        raise NotImplementedError

    def reader(self):
        raise NotImplementedError

    def writer(self):
        raise NotImplementedError
