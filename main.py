import socket
import RPi.GPIO as GPIO
import json

info = json.loads(
    '{"manufacturer": "Volkswagen", "model": "Golf", "color": "White", "plate": "0000 AAA"}')


def sendSorry(channel):
    print("message sent")
    coche1.sendto(bytes("Sorry! by {} {} ({})".format(
        info["manufacturer"], info["model"], info["color"]), encoding='utf8'),
        ('192.168.1.255', 1050))


sButton = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(sButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(sButton, GPIO.FALLING,
                      callback=sendSorry, bouncetime=1000)

coche1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
coche1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
coche1.bind(('', 1050))
# coche1.settimeout(0.2)
while True:
    print("Receiving...")
    message, sender = coche1.recvfrom(1024)
    print(message)
