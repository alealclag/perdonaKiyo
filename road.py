import socket

location = "A-4 Km. 455"
speedLimit = 100
vehicleBD = False
accident = False
roadWork = False
otherIncident = False

# Configuración del socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', 1060))
sock.settimeout(1)

print("Starting road system...")

while True:
    try:
        sock.sendto(bytes("2/{}".format(speedLimit), encoding='utf8'),
                    ('192.168.1.255', 1050))
    except BlockingIOError:
        pass

    try:
        message, sender = sock.recvfrom(1024)
        messageArray = str(message.decode("utf-8")).split("/")

        if messageArray[0] == "3.1":
            vehicleBD = True
        elif messageArray[0] == "3.2":
            accident = True
            # Enviar Alerta a emergencias
    except BlockingIOError:
        pass
