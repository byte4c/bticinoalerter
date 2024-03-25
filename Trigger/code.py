import os
import socketpool
import wifi

import ssl
import adafruit_requests

# Get WiFi details, ensure these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# Initialize WiFi Pool (There can be only 1 pool & top of script)
radio = wifi.radio
pool = socketpool.SocketPool(radio)

print("Connecting to AP...")
while not wifi.radio.ipv4_address:
    try:
        wifi.radio.connect(ssid, password)
    except ConnectionError as e:
        print("could not connect to AP, retrying: ", e)
print("Connected to", str(radio.ap_info.ssid, "utf-8"), "\tRSSI:", radio.ap_info.rssi)

# Initialize a requests session
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

TEXT_URL = "http://192.168.20.10/alert"

print("-" * 40)
print("Fetching text from %s" % TEXT_URL)
response = requests.get(TEXT_URL)
print("Text Response: ", response.text)
print("-" * 40)
response.close()