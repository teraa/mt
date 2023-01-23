import errno
import logging
from scapy.layers.inet import *
from queue import Queue


def socket_catch(func):
    def w(*args):
        try:
            func(*args)
        except socket.error as e:
            logging.error(str(e))
            if e.errno == errno.EBADF:  # exiting
                return False
            if e.errno == errno.EINTR:  # interrupt
                return True

        return True

    return w


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
        logging.debug('Start')
        while self.read():
            pass

    def writer(self):
        logging.debug('Start')
        while self.write():
            pass

    def read(self) -> bool:
        raise NotImplementedError()

    def write(self) -> bool:
        raise NotImplementedError()
