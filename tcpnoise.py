import logging
import optparse
import socket
import threading
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
        
        def writer():
            i = 0
            while True:
                logging.info(f'send: {i}')
                sock.sendall(str.encode(str(i) + '\n'))
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
