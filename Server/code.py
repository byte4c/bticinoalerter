import time
import board
import microcontroller
import neopixel
import digitalio
import os
import socketpool
import wifi

from adafruit_httpserver import Server, Request, Response, FileResponse

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

def handle_battery(battery: any):
    print("Battery: ", "{}, {}\n".format(time.time(), battery))
    try:
        with open("/battery.txt", "a") as sdc:
            sdc.write("{}, {}\n".format(time.time(), battery))
            sdc.close()
    except OSError as e:
        print(e)
        pass
    except RuntimeError as e:
        print(e)
        pass

def handle_battery_reset():
    try:
        with open("/battery.txt", "w") as sdc:
            sdc.write("Reset at {}\n".format(time.time()))
            sdc.close()
    except OSError as e:
        print(e)
        pass
    except RuntimeError as e:
        print(e)
        pass

button = digitalio.DigitalInOut(PINBUTTON)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

print("Connecting to ", os.getenv("CIRCUITPY_WIFI_SSID"))
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print("Connected to ", os.getenv("CIRCUITPY_WIFI_SSID"))

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool)

@server.route("/alert")
def alert_handler(request: Request):
    print("Recieved alert message: ", request.body.decode())
    handle_battery(request.query_params.get('battery'))
    global ALERTTRIGGERED
    ALERTTRIGGERED = True
    global ALERTSTATUS
    if ALERTSTATUS != 0:
        ALERTSTATUS = 2
        global LASTALERT
        LASTALERT = time.monotonic()
        return Response(request, f"Alert recieved! ({request.body.decode()})")
    else:
        return Response(request, f"Alert ignored. ({request.body.decode()})")

@server.route("/status")
def status_handler(request: Request):
    print("Recieved status request")
    global ALERTSTATUS
    if ALERTSTATUS == 0:
        return Response(request, f"Status: OFF")
    elif ALERTSTATUS == 1:
        return Response(request, f"Status: STANDBY")
    elif ALERTSTATUS == 2:
        return Response(request, f"Status: ALERT")

@server.route("/battery")
def battery_handler(request: Request):
    print("Recieved battery request")
    return FileResponse(request, filename='battery.txt', root_path='/')

@server.route("/battery/clear")
def battery_reset_handler(request: Request):
    print("Recieved battery reset request")
    handle_battery_reset()
    return Response(request, f"Battery file cleared")

print("starting server..")
try:
    server.start(str(wifi.radio.ipv4_address), 80)
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
