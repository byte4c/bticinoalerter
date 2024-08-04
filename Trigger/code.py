import os
import socketpool
import wifi 
import ssl
import adafruit_requests 
import alarm
import board

ALERT_URL = "http://192.168.20.10/alert"

radio = wifi.radio
pool = socketpool.SocketPool(radio)

def alert(url):
    print("Connecting to AP...")
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
        except ConnectionError as e:
            print("could not connect to AP, retrying: ", e)
    print("Connected to", str(radio.ap_info.ssid, "utf-8"), "\tRSSI:", radio.ap_info.rssi)

    ssl_context = ssl.create_default_context()
    requests = adafruit_requests.Session(pool, ssl_context)

    print("-" * 40)
    print("Fetching text from %s" % url)
    response = requests.get(url)
    print("Text Response: ", response.text)
    print("-" * 40)
    response.close()

# Print out which alarm woke us up, if any.
print(alarm.wake_alarm)

print("Starting program")
alert(ALERT_URL)

pin_alarm = alarm.pin.PinAlarm(pin=board.D0, value=False, pull=True)
alarm.exit_and_deep_sleep_until_alarms(pin_alarm)