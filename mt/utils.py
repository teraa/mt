import errno
import logging
import signal
import sys


def _handler(sig, frame):
    print('\nExiting...')
    sys.exit(0)


def sighandler():
    return signal.signal(signal.SIGINT, _handler)


def socket_guard(func):
    def _(*args):
        try:
            return func(*args)

        except OSError as e:
            if e.errno == errno.EINTR:  # interrupt
                return True
            if e.errno == errno.EBADF:  # exiting
                return False

            logging.exception(e)
            raise

    return _
