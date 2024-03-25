import time
import board
import microcontroller
import neopixel
import digitalio
import os
import socketpool
import wifi

from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer

ALERTTRIGGERED = False
ALERTSTATUS = 0 # 0=OFF 1=STANDBY 2=ON
LASTALERT = time.monotonic()
ALERTDURATION = 300

PINBUTTON = board.GP16
PINPIXELS = board.GP0  # This is the default pin on the 5x5 NeoPixel Grid BFF.
NUMPIXELS = 16  # Update this to match the number of LEDs.
BRIGHTNESS = 0.75  # A number between 0.0 and 1.0, where 0.0 is off, and 1.0 is max.
SPEED = 0.5  # Increase to slow down the rainbow. Decrease to speed it up.

pixels = neopixel.NeoPixel(PINPIXELS, NUMPIXELS, brightness=BRIGHTNESS, auto_write=False)

def show_color(color: tuple[int, int, int], duration: int, reset: bool = True):
    pixels.fill(color)
    pixels.show()
    time.sleep(duration)
    if reset:
        pixels.fill(0)
        pixels.show()

button = digitalio.DigitalInOut(PINBUTTON)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

print("Connecting to ", os.getenv("CIRCUITPY_WIFI_SSID"))
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print("Connected to ", os.getenv("CIRCUITPY_WIFI_SSID"))

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)

@server.route("/alert")
def alert_handler(request: HTTPRequest):
    print("Recieved alert message: ", request.body.decode())
    global ALERTTRIGGERED
    ALERTTRIGGERED = True
    global ALERTSTATUS
    if ALERTSTATUS != 0:
        ALERTSTATUS = 2
        global LASTALERT
        LASTALERT = time.monotonic();
        with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
            response.send(f"Alert recieved! ({request.body.decode()})")
    else:
        with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
            response.send(f"Alert ignored. ({request.body.decode()})")

@server.route("/status")
def status_handler(request: HTTPRequest):
    print("Recieved status request")
    global ALERTSTATUS
    if ALERTSTATUS == 0:
        with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
            response.send(f"Status: OFF")
    elif ALERTSTATUS == 1:
        with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
            response.send(f"Status: STANDBY")
    elif ALERTSTATUS == 2:
        with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
            response.send(f"Status: ALERT")

print("starting server..")
try:
    server.start(str(wifi.radio.ipv4_address))
    print(f"Listening on http://{wifi.radio.ipv4_address}:80")
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()

show_color((0, 0, 0), 0, False)
while True:
    try:
        server.poll()
        if not button.value:
            if ALERTSTATUS == 0:
                # Standby
                print("Alert set to STANDBY")
                ALERTSTATUS = 1
                show_color((0, 255, 0), 1)
            elif ALERTSTATUS == 1:
                # Off
                print("Alert set to OFF")
                ALERTSTATUS = 0
                show_color((255, 0, 0), 1)
            elif ALERTSTATUS == 2:
                # Standby after alert
                print("Alert reset")
                ALERTSTATUS = 1
                show_color((255, 165, 0), 1)

        if ALERTTRIGGERED:
            print(f"Alert triggered")
            show_color((0, 0, 255), SPEED, False)
            show_color((255, 0, 0), SPEED, False)
            show_color((0, 0, 0), 0, False)
            ALERTTRIGGERED = False


        if ALERTSTATUS == 2:
            alertduration = time.monotonic() - LASTALERT
            print(f"ALERT!!! {alertduration}")
            show_color((0, 0, 255), SPEED, False)
            show_color((255, 0, 0), SPEED, False)
            if alertduration > ALERTDURATION:
                print("Alert timeout")
                ALERTSTATUS = 1
                show_color((0, 0, 0), 0, False)
    
    except Exception as e:
        print(e)
        continue
