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
vehicleIncidentList = []
rwList = []
otherIncidentList = []


def sendSpeed():
    try:
        sock.sendto(bytes("2/{}".format(speedLimit), encoding='utf8'),
                    ('192.168.1.255', 1050))
    except BlockingIOError:
        pass


def sendIncidents():

    try:
        if roadWork:
            for id in rwList:
                sock.sendto(bytes("3.3/{}".format(id), encoding='utf8'),
                            ('192.168.1.255', 1050))
        if otherIncident:
            for id in otherIncidentList:
                sock.sendto(bytes("3.4/{}".format(id), encoding='utf8'),
                            ('192.168.1.255', 1050))

    except BlockingIOError:
        pass


def recvMessage():
    try:
        message, sender = sock.recvfrom(1024)
        messageArray = str(message.decode("utf-8")).split("/")

        if messageArray[0] == "3.1":
            vehicleIncidentList.append(messageArray[2])
            signMessage.value = "Breakdown {} nearby".format(messageArray[1])

        elif (messageArray[0] == "3.1.0") or (messageArray[0] == "3.2.0"):
            vehicleIncidentList.remove(messageArray[1])
            signMessage.value = ""

        elif messageArray[0] == "3.2":
            vehicleIncidentList.append(messageArray[2])
            signMessage.value = "Accident {} nearby".format(messageArray[1])

    except BlockingIOError:
        pass


def submitRoadWork():
    global roadWork
    if not (rwTextBox.value == ""):
        rwList.append(rwTextBox.value)
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
    except ValueError:
        pass


def submitOtherIncident():
    global otherIncident
    if not (otherIncidentTextBox.value == ""):
        otherIncidentList.append(otherIncidentTextBox.value)
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
    except ValueError:
        pass


def submitSpeedLimit():
    global speedLimit
    speedLimit = int(speedLimitTextBox.value)
    speedLimitIndicator.value = "Speed Limit: {} Km/h".format(speedLimit)
    speedLimitTextBox.value = ""


# Configuración del socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', 1060))
sock.settimeout(0)


roadGui = App(title="perdonaKiyo")

rwTextBox = TextBox(roadGui)
rwButton = PushButton(
    roadGui, command=submitRoadWork, text="Submit roadwork")
removeRwButton = PushButton(
    roadGui, command=removeRoadWork, text="Remove roadwork")

otherIncidentTextBox = TextBox(roadGui)
otherIncButton = PushButton(
    roadGui, command=submitOtherIncident, text="Submit other incident")
removeOtherIncButton = PushButton(
    roadGui, command=removeOtherIncident, text="Remove other incident")

speedLimitTextBox = TextBox(roadGui)
speedLimButton = PushButton(
    roadGui, command=submitSpeedLimit, text="Submit Speed Limit")

rwListText = Text(roadGui, text=rwList)
otherIncidentListText = Text(roadGui, text=otherIncidentList)

signMessage = Text(roadGui)

speedLimitIndicator = Text(
    roadGui, text="Speed Limit: {} Km/h".format(speedLimit))

roadGui.repeat(1000, recvMessage)
roadGui.repeat(1000, sendSpeed)
roadGui.repeat(1000, sendIncidents)

roadGui.display()
