import errno
import logging


def socket_guard(func):
    def socket_guard(*args):
        try:
            func(*args)
            return True

        except OSError as e:
            if e.errno == errno.EINTR:  # interrupt
                return True
            if e.errno == errno.EBADF:  # exiting
                return False

            logging.exception(e)
            raise

    return socket_guard
