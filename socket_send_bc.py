import socket
import sys
import time


def broadcast(frequency, port):

    server = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.2)

    while True:
        server.sendto(b"prueba", ('<broadcast>', port))
        print("message sent...")
        time.sleep(frequency)


broadcast(5, 1000)
