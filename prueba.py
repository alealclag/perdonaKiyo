import socket
import time


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', 1050))
sock.settimeout(0)

while True:
    time.sleep(1)
    try:
        message = sock.recvfrom(1024)
        print(message)
    except:
        pass
