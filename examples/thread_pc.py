import queue
import sys
import threading
import time
import sighandler

q = queue.Queue()


def producer():
    print(f'Producer {q=}')

    n = 0
    while True:
        time.sleep(1)
        q.put(n)
        debug(f'Producer: {n=}')
        n = n + 1


def consumer():
    print(f'Consumer {q=}')

    while True:
        n = q.get()
        debug(f'Consumer: {n=}')
        q.task_done()


def main():
    sighandler.register()

    p = threading.Thread(target=producer, daemon=True)
    c = threading.Thread(target=consumer, daemon=True)
    p.start()
    c.start()
    p.join()
    c.join()

    print('End')


debug_lock = threading.Lock()


def debug(message):
    debug_lock.acquire()
    print(message, file=sys.stderr)
    debug_lock.release()


if __name__ == '__main__':
    main()
