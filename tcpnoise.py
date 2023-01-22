import logging
import optparse
import socket
import time
import sighandler


def main():
    sighandler.register()
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d %(levelname)s] %(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')

    parser = optparse.OptionParser()
    parser.add_option('-p', dest='port', type='int', default=55555, help='server port [%default]')
    parser.add_option('-H', dest='host', default='10.20.0.1', help='server address [%default]')
    parser.add_option('-i', dest='interval', type='float', default=5, help='server address [%default]')
    opt, args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((opt.host, opt.port))
        i = 0
        while True:
            logging.debug(i)
            sock.sendall(str.encode(str(i) + '\n'))
            i = i + 1
            time.sleep(opt.interval)


if __name__ == '__main__':
    main()
