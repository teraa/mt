import signal
import sys


def handler(sig, frame):
    print('\nExiting...')
    sys.exit(0)


def register():
    return signal.signal(signal.SIGINT, handler)
