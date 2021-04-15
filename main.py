import socket
import RPi.GPIO as GPIO
import json
import os

# Carga de la información del vehículo
info = json.load(
    open("Vehicle Information Files/{}.json".format(socket.gethostname())))
myPlate = info["plate"]
myip = os.popen("ip -4 route show default").read().split()[8]
speedLimit = 120

# Callback de la interrupción, que manda en broadcast la señal de disculpa


def sendSorry(channel):
    print("message sent")
    # Al principio del mensaje se añade un código que añade el tipo de mensaje (Ver archivo "Messages_code.txt" para más información)
    sock.sendto(bytes("1/Sorry! by {} {} ({})/{}".format(
        info["manufacturer"], info["model"], info["color"], info["plate"]), encoding='utf8'),
        ('192.168.1.255', 1050))


# Configuración de la interrupción en GPIO
sButton = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(sButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(sButton, GPIO.FALLING,
                      callback=sendSorry, bouncetime=1000)

# Configuración del socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', 1050))
sock.settimeout(0)

print("Starting reception of messages..")

# Bucle para la recepción de señales
while True:
    try:
        message, sender = sock.recvfrom(1024)
        messageArray = str(message.decode("utf-8")).split("/")

        if messageArray[0] == "1":
            senderPlate = messageArray[2]
            if senderPlate != myPlate:
                print(messageArray[1])
        elif messageArray[0] == "2":
            speedLimit = int(messageArray[1])
        elif messageArray[0] == "3.1":
            print(messageArray[1])
        elif messageArray[0] == "3.2":
            print(messageArray[1])
        elif messageArray[0] == "3.3":
            print(messageArray[1])
    except BlockingIOError:
        pass
