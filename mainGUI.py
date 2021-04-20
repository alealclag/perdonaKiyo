import socket
import json
from guizero import App, PushButton, Text, Slider, Box
import time

# Carga de la información del vehículo
info = json.load(
    open("Vehicle Information Files/{}.json".format(socket.gethostname())))
myPlate = info["plate"]
speedLimit = 120
speed = 0
broken = False
accidented = False
vehicleIncidentLog = [myPlate]
roadWorkLog = []
incidentLog = []
cont = 0


def sendSorry():
    print("Sorry sent")
    sock.sendto(bytes("1/{}/{}/{}/{}".format(
        info["manufacturer"], info["model"], info["color"], info["plate"]), encoding='utf8'),
        ('192.168.1.255', 1050))


def sendBreakDown():

    sock.sendto(bytes(
        "3.1/{}/{}".format(info["type"], info["plate"]), encoding='utf8'), ('192.168.1.255', 1050))


def endBreakDown():
    sock.sendto(
        bytes("3.1.0/{}".format(info["plate"]), encoding='utf8'), ('192.168.1.255', 1050))


def sendAccident():
    sock.sendto(
        bytes("3.2/{}/{}".format(info["type"], info["plate"]), encoding='utf8'), ('192.168.1.255', 1050))


def endAccident():
    sock.sendto(
        bytes("3.2.0/{}".format(info["plate"]), encoding='utf8'), ('192.168.1.255', 1050))


def toggleBroken():
    global broken
    broken = not broken
    if broken:
        breakdownButton.text_color = "red"
        accidentButton.text_color = "black"
        sendBreakDown()
        endAccident()
    else:
        breakdownButton.text_color = "black"
        endBreakDown()


def toggleAccident():
    global accidented
    accidented = not accidented
    if accidented:
        accidentButton.text_color = "red"
        breakdownButton.text_color = "black"
        sendAccident()
        endBreakDown()
    else:
        accidentButton.text_color = "black"
        endAccident()


def throttleController(slider_value):
    global speed
    global speedLimit
    speed = slider_value
    speedIndicator.value = "Speed: {} Km/h".format(speed)

    if int(speed) > int(speedLimit):
        speedIndicator.text_color = "red"
    else:
        speedIndicator.text_color = "black"


def recvMessage():
    global speedLimit
    try:
        message, sender = sock.recvfrom(1024)
        messageArray = str(message.decode("utf-8")).split("/")

        # Señal de perdón
        if (messageArray[0] == "1") and (messageArray[4] != myPlate):
            gui.info("Sorry!", "Sorry! by {} {} ({})".format(
                messageArray[1], messageArray[2], messageArray[3]))

        # Límite de velocidad
        elif messageArray[0] == "2":
            speedLimit = int(messageArray[1])
            try:
                speedLimitIndicator.value = "Speed Limit: {} Km/h".format(
                    speedLimit)
                if int(speed) > int(speedLimit):
                    speedIndicator.text_color = "red"
                else:
                    speedIndicator.text_color = "black"
            except:
                pass

        # Incidencia Avería
        elif (messageArray[0] == "3.1") and not(messageArray[2] in vehicleIncidentLog):
            vehicleIncidentLog.append(messageArray[2])
            gui.info("Breakdown Warning",
                     "Broken {} nearby".format(messageArray[1]))

        # Incidencia Accidente
        elif (messageArray[0] == "3.2") and not(messageArray[2] in vehicleIncidentLog):
            vehicleIncidentLog.append(messageArray[2])
            gui.info("Accident Alert",
                     "Accidented {} nearby".format(messageArray[1]))

        # Obra
        elif (messageArray[0] == "3.3") and not(messageArray[1] in roadWorkLog):
            roadWorkLog.append(messageArray[1])
            gui.info("Roadwork Warning", "Roadwork nearby")

        # Incidencia
        elif (messageArray[0] == "3.4") and not(messageArray[1] in incidentLog):
            incidentLog.append(messageArray[1])
            gui.info("Incident Warning", "Incident nearby")

    except BlockingIOError:
        pass


def sendWarningOrAlert():
    try:
        if broken:
            sendBreakDown()
        elif accidented:
            sendAccident()

    except BlockingIOError:
        pass


# Configuración del socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', 1050))
sock.settimeout(0)


# Interfaz gráfica
gui = App(title="perdonaKiyo")

buttonsBox = Box(gui, width="50", align="top", layout="grid", border=True)

sorryButton = PushButton(
    buttonsBox, command=sendSorry, text="Sorry!", grid=[0, 0])

buttonsBox2 = Box(gui, width="50", align="top", layout="grid", border=True)
breakdownButton = PushButton(
    buttonsBox2, command=toggleBroken, text="Breakdown", grid=[1, 0])
accidentButton = PushButton(
    buttonsBox2, command=toggleAccident, text="Accident", grid=[2, 0])

speedBox = Box(gui, align="bottom", border=True)
throttle = Slider(speedBox, command=throttleController, start=0, end=180)
speedIndicator = Text(speedBox, text="Speed: {} Km/h".format(speed))
speedLimitIndicator = Text(
    speedBox, text="Speed Limit: {} Km/h".format(speedLimit))


gui.repeat(1000, recvMessage)
gui.repeat(1000, sendWarningOrAlert)

gui.display()
