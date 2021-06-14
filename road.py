import socket
import time
from guizero import App, PushButton, Text, Slider, Box, TextBox
from datetime import datetime
import smtplib
import ssl

location = "A-4 Km. 455"
speedLimit = 120
breakdown = False
accident = False
roadWork = False
otherIncident = False
rwList = set()
otherIncidentList = set()
brAddress = '192.168.1.255'
sentEmail = False
accidentList = set()
BDList = set()
emailSentList = set()


def checkRWorInc():
    if (not accident) and (not breakdown):
        if roadWork:
            signMessage.value = "Roadwork nearby"
        elif otherIncident:
            signMessage.value = "Incident nearby"


def sendAccidentEmail(vehicle):
    global location
    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("a4road455@gmail.com", "perdonaKiyo2021")
        if vehicle == "":
            server.sendmail("a4road455@gmail.com", "alalla@hotmail.es",
                            "Accident at {}".format(location))
        else:
            server.sendmail("a4road455@gmail.com", "alalla@hotmail.es",
                            "{} accident at {}".format(vehicle, location))


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
    global accident, emailSentList
    try:
        message, sender = sock.recvfrom(1024)
        messageArray = str(message.decode("utf-8")).split("/")

        if messageArray[0] == "3.1":
            BDList.add(messageArray[2])
            breakdown = True
            if not accident:
                signMessage.value = "Broken {} nearby".format(messageArray[1])

        elif messageArray[0] == "3.1.0":
            BDList.remove(messageArray[1])
            if not BDList:
                signMessage.value = ""
                breakdown = False
                checkRWorInc()

        elif messageArray[0] == "3.2.0":
            accidentList.remove(messageArray[1])
            emailSentList.remove(messageArray[1])
            if not accidentList:
                signMessage.value = ""
                accident = False
                checkRWorInc()

        elif messageArray[0] == "3.2":
            accidentList.add(messageArray[2])
            signMessage.value = "Accidented {} nearby".format(messageArray[1])
            accident = True
            for accidentPlate in accidentList:
                if accidentPlate not in emailSentList:
                    sendAccidentEmail(messageArray[1])
                    emailSentList.add(messageArray[2])

    except BlockingIOError:
        pass


def submitRoadWork():
    global roadWork
    if not (rwTextBox.value == ""):
        rwList.add(rwTextBox.value)
        rwListText.value = rwList
        rwTextBox.value = ""
        roadWork = True
        checkRWorInc()


def removeRoadWork():
    try:
        global roadWork
        rwList.remove(rwTextBox.value)
        rwListText.value = rwList
        rwTextBox.value = ""
        if not rwList:
            roadWork = False
            rwListText.value = ""
            signMessage.value = ""
            checkRWorInc()
    except KeyError:
        pass


def submitOtherIncident():
    global otherIncident
    if not (otherIncidentTextBox.value == ""):
        otherIncidentList.add(otherIncidentTextBox.value)
        otherIncidentListText.value = otherIncidentList
        otherIncidentTextBox.value = ""
        otherIncident = True
        checkRWorInc()


def removeOtherIncident():
    try:
        global otherIncident
        otherIncidentList.remove(otherIncidentTextBox.value)
        otherIncidentListText.value = otherIncidentList
        otherIncidentTextBox.value = ""
        if not otherIncidentList:
            otherIncident = False
            otherIncidentListText.value = ""
            signMessage.value = ""
            checkRWorInc()
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

accidentButton = PushButton(
    roadGui, command=sendAccidentEmail, args=[""], text="Send alert to emergencies")

roadGui.repeat(500, recvMessage)
roadGui.repeat(2000, sendSpeed)
roadGui.repeat(5000, sendIncidents)

roadGui.display()
