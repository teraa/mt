import errno
import os
import signal
import sys
import threading

from loguru import logger as logging


def _handler(sig, frame):
    print('\nExiting...')
    sys.exit(0)


def sighandler():
    return signal.signal(signal.SIGINT, _handler)

def excepthook(args: threading.ExceptHookArgs):
    logging.exception(args.exc_value)
    os._exit(1)

def socket_guard(func):
    def _(*args):
        try:
            return func(*args)

        except OSError as e:
            if e.errno == errno.EINTR:  # interrupt
                return True
            if e.errno == errno.EBADF:  # exiting
                return False

            raise

    return _
