import optparse
import signal
import socket
import threading
import time

from loguru import logger as logging

from mt.utils import sighandler


def main():
    signal.signal(signal.SIGINT, sighandler)

    parser = optparse.OptionParser()
    parser.add_option('-p', dest='port', type='int', default=55555, help='server port [%default]')
    parser.add_option('-H', dest='host', default='10.20.0.1', help='server address [%default]')
    parser.add_option('-i', dest='interval', type='float', default=5, help='server address [%default]')
    opt, args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((opt.host, opt.port))
        
        def writer():
            i = 0
            while True:
                message = f'message {i}'
                logging.info(f'send: {message}')
                sock.sendall(str.encode(message + '\n'))
                i = i + 1
                time.sleep(opt.interval)
        
        def reader():
            while True:
                data = sock.recv(65535)
                logging.info(f'recv: {bytes.decode(data).strip()}')
        
        w = threading.Thread(target=writer, name='Writer', daemon=True)
        r = threading.Thread(target=reader, name='Reader', daemon=True)

        w.start()
        r.start()

        w.join()
        r.join()


if __name__ == '__main__':
    main()
