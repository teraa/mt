class Base(object):
    def __init__(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        raise NotImplementedError()

    def reader(self):
        while self._read():
            pass

    def writer(self):
        while self._write():
            pass

    def _read(self) -> bool:
        raise NotImplementedError()

    def _write(self) -> bool:
        raise NotImplementedError()
