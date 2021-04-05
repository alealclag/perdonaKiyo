import socket
import RPi.GPIO as GPIO
import json
import os

# Carga de la información del vehículo
info = json.load(open("{}.json".format(socket.gethostname())))
myip = os.popen("ip -4 route show default").read().split()[8]


# Callback de la interrupción, que manda en broadcast la señal de disculpa
def sendSorry(channel):
    print("message sent")
    sock.sendto(bytes("Sorry! by {} {} ({})".format(
        info["manufacturer"], info["model"], info["color"]), encoding='utf8'),
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
# coche1.settimeout(0.2)


# Bucle para la recepción de señales
while True:
    print("Receiving...")
    message, sender = sock.recvfrom(1024)
    senderIp = str(sender).split("'")[1]
    if senderIp != myip:
        print(message.decode("utf-8"))
