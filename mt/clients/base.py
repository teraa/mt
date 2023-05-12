from mt.tunnel import NetworkPipe


class Base(object):
    def __init__(self, pipe: NetworkPipe) -> None:
        self._pipe = pipe

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        raise NotImplementedError()

    def reader(self):
        while self.read():
            pass

    def writer(self):
        while self.write():
            pass

    def read(self) -> bool:
        raise NotImplementedError()

    def write(self) -> bool:
        raise NotImplementedError()
