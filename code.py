import ssl
import board
import digitalio
import time
from adafruit_datetime import datetime

import wifi
import adafruit_requests
import socketpool
from adafruit_portalbase.network import NetworkBase
from secrets import secrets

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

wifi.radio.connect(secrets['ssid'], secrets['password'])
pool = socketpool.SocketPool(wifi.radio)
print("My IP address is", wifi.radio.ipv4_address)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

try:
    import rtc
    response = requests.get("http://worldclockapi.com/api/json/utc/now")
    dtstr = response.json()['currentDateTime']
    parsed = datetime.fromisoformat(dtstr[:-1])
    rtc.RTC().datetime = parsed.timetuple()
except Exception as e:
    print(e)

response = requests.get("https://api.sunrise-sunset.org/json?lat=51.283970&lng=0.172400&formatted=0")
dtstr = response.json()['results']['nautical_twilight_end']

sunset = datetime.fromisoformat(dtstr)

while True:
    print(parsed)
    print(datetime.now())

    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(2)
    print("whatever")