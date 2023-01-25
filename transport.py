import errno
import logging
from scapy.layers.inet import *
from queue import Queue


def socket_guard(func):
    def socket_guard(*args):
        try:
            func(*args)
            return True
            
        except OSError as e:
            if e.errno == errno.EINTR: # interrupt
                return True
            if e.errno == errno.EBADF:  # exiting
                return False

            logging.exception(e)
            raise

    return socket_guard


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
        while self._read():
            pass

    def writer(self):
        while self._write():
            pass

    def _read(self) -> bool:
        raise NotImplementedError()

    def _write(self) -> bool:
        raise NotImplementedError()
