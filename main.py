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
broken = False
accidented = False
vehicleincidentLog = {}
roadWorkLog = {}
incidentLog = {}

# Callback de la interrupción, que manda en broadcast la señal de disculpa


def sendSorry(channel):
    print("Sorry sent")
    # Al principio del mensaje se añade un código que añade el tipo de mensaje (Ver archivo "Messages_code.txt" para más información)
    sock.sendto(bytes("1/Sorry! by {} {} ({})/{}".format(
        info["manufacturer"], info["model"], info["color"], info["plate"]), encoding='utf8'),
        ('192.168.1.255', 1050))


def sendBreakDown():
    sock.sendto(bytes("3.1/{} breakdown nearby/{}".format(info["type"], info["plate"]), encoding='utf8'),
                ('192.168.1.255', 1050))


def toggleBreakDownWarning(channel):
    global broken
    broken = not broken
    if broken:
        accidented = False
        print("Sending breakdown warning")
        sock.sendto(bytes("3.1", encoding='utf8'), ('192.168.1.1', 1060))
        sendBreakDown()


def sendAccident():
    sock.sendto(bytes("3.2/Accident nearby/{}".format(info["plate"]), encoding='utf8'),
                ('192.168.1.255', 1050))


def toggleAccidentAlert(channel):
    global accidented
    accidented = not accidented
    if accidented:
        broken = False
        print("Sending Accident Alert")
        sock.sendto(bytes("3.1", encoding='utf8'), ('192.168.1.1', 1060))
        sendAccident()


# Configuración de la interrupción en GPIO
sButton = 16
bdButton = 20
aButton = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bdButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(aButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(sButton, GPIO.FALLING,
                      callback=sendSorry, bouncetime=1000)
GPIO.add_event_detect(bdButton, GPIO.FALLING,
                      callback=toggleBreakDownWarning, bouncetime=1000)
GPIO.add_event_detect(aButton, GPIO.FALLING,
                      callback=toggleAccidentAlert, bouncetime=1000)

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

        if messageArray[0] == "1":  # Señal de perdón
            if messageArray[2] != myPlate:
                print(messageArray[1])

        elif messageArray[0] == "2":  # Límite de velocidad
            speedLimit = int(messageArray[1])

        elif messageArray[0] == "3.1":  # Incidencia Avería
            if (messageArray[2] != myPlate) and not(messageArray[2] in vehicleincidentLog):
                print(messageArray[1])
                vehicleincidentLog.add(messageArray[2])

        elif messageArray[0] == "3.2":  # Incidencia Accidente
            if (messageArray[2] != myPlate) and not(messageArray[2] in vehicleincidentLog):
                print(messageArray[1])
                vehicleincidentLog.add(messageArray[2])

        elif messageArray[0] == "3.3":  # Obra
            if not(messageArray[2] in roadWorkLog):
                print(messageArray[1])
                roadWorkLog.add(messageArray[2])

        elif messageArray[0] == "3.4":  # Incidencia
            if not(messageArray[2] in incidentLog):
                print(messageArray[1])
                incidentLog.add(messageArray[2])

    except BlockingIOError:
        pass

    try:
        if broken:
            sendBreakDown()
        elif accidented:
            sendAccident()

    except BlockingIOError:
        pass
