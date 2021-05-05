import socket
import time
from guizero import App, PushButton, Text, Slider, Box, TextBox
from datetime import datetime
location = "A-4 Km. 455"
speedLimit = 120
breakdown = False
accident = False
roadWork = False
otherIncident = False
rwList = set()
otherIncidentList = set()
brAddress = '192.168.0.255'


def sendSpeed():
    try:
        sock.sendto(bytes("2/{}".format(speedLimit), encoding='utf8'),
                    (brAddress, 1050))

    except BlockingIOError:
        pass


def sendIncidents():

    try:
        if roadWork:
            for id in rwList:
                sock.sendto(bytes("3.3/{}".format(id), encoding='utf8'),
                            (brAddress, 1050))

        if otherIncident:
            for id in otherIncidentList:
                sock.sendto(bytes("3.4/{}".format(id), encoding='utf8'),
                            (brAddress, 1050))

    except BlockingIOError:
        pass


def recvMessage():
    global accident
    try:
        message, sender = sock.recvfrom(1024)
        messageArray = str(message.decode("utf-8")).split("/")

        if messageArray[0] == "3.1" and not accident:
            signMessage.value = "Broken {} nearby".format(messageArray[1])

        elif messageArray[0] == "3.1.0":
            signMessage.value = ""

        elif messageArray[0] == "3.2.0":
            signMessage.value = ""
            accident = False

        elif messageArray[0] == "3.2":
            signMessage.value = "Accidented {} nearby".format(messageArray[1])
            accident = True

    except BlockingIOError:
        pass


def submitRoadWork():
    global roadWork
    if not (rwTextBox.value == ""):
        rwList.add(rwTextBox.value)
        rwListText.value = rwList
        rwTextBox.value = ""
        roadWork = True


def removeRoadWork():
    try:
        global roadWork
        rwList.remove(rwTextBox.value)
        rwListText.value = rwList
        rwTextBox.value = ""
        if not rwList:
            roadWork = False
            rwListText.value = ""
    except KeyError:
        pass


def submitOtherIncident():
    global otherIncident
    if not (otherIncidentTextBox.value == ""):
        otherIncidentList.add(otherIncidentTextBox.value)
        otherIncidentListText.value = otherIncidentList
        otherIncidentTextBox.value = ""
        otherIncident = True


def removeOtherIncident():
    try:
        global otherIncident
        otherIncidentList.remove(otherIncidentTextBox.value)
        otherIncidentListText.value = otherIncidentList
        otherIncidentTextBox.value = ""
        if not otherIncidentList:
            otherIncident = False
            otherIncidentListText.value = ""
    except KeyError:
        pass


def submitSpeedLimit():
    global speedLimit
    try:
        speedLimit = int(speedLimitTextBox.value)
        speedLimitIndicator.value = "Speed Limit: {} Km/h".format(speedLimit)
        speedLimitTextBox.value = ""
    except ValueError:
        pass


# Configuración del socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', 1050))
sock.settimeout(0)


roadGui = App(title="perdonaKiyo")

rwBox = Box(roadGui, align="left")
rwTextBox = TextBox(rwBox)
rwButton = PushButton(
    rwBox, command=submitRoadWork, text="Submit roadwork")
removeRwButton = PushButton(
    rwBox, command=removeRoadWork, text="Remove roadwork")

otherIncidentBox = Box(roadGui, align="right")
otherIncidentTextBox = TextBox(otherIncidentBox)
otherIncButton = PushButton(
    otherIncidentBox, command=submitOtherIncident, text="Submit other incident")
removeOtherIncButton = PushButton(
    otherIncidentBox, command=removeOtherIncident, text="Remove other incident")


speedLimButton = PushButton(
    roadGui, command=submitSpeedLimit, text="Submit Speed Limit", align="bottom")
speedLimitTextBox = TextBox(roadGui, align="bottom")

signMessage = Text(roadGui)
voidLabel = Text(roadGui, text="")
speedLimitIndicator = Text(
    roadGui, text="Speed Limit: {} Km/h".format(speedLimit))
voidLabel = Text(roadGui, text="")
rwLabel = Text(roadGui, text="Roadwork:")
rwListText = Text(roadGui)
voidLabel = Text(roadGui, text="")
otherIncidentsLabel = Text(roadGui, text="Other Incidents:")
otherIncidentListText = Text(roadGui)
voidLabel = Text(roadGui, text="")

roadGui.repeat(500, recvMessage)
roadGui.repeat(2000, sendSpeed)
roadGui.repeat(5000, sendIncidents)

roadGui.display()
