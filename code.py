
import alarm
import ssl
import board
import digitalio
import time
from adafruit_datetime import datetime, timedelta, date

import wifi
import adafruit_requests
import socketpool
from adafruit_portalbase.network import NetworkBase
from secrets import secrets

from digitalio import Pull

from microcontroller import Pin


led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

wifi.radio.connect(secrets['ssid'], secrets['password'])
pool = socketpool.SocketPool(wifi.radio)
print("My IP address is", wifi.radio.ipv4_address)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

import rtc
response = requests.get("http://worldclockapi.com/api/json/utc/now")
dtstr = response.json()['currentDateTime']
parsed = datetime.fromisoformat(dtstr[:-1])
rtc.RTC().datetime = parsed.timetuple()

response = requests.get("https://api.sunrise-sunset.org/json?lat=51.283970&lng=0.172400&formatted=0&date=%s" % str(date.today()))
dtstr = response.json()['results']['nautical_twilight_end']

sunset = datetime.fromisoformat(dtstr).replace(tzinfo=None)
print(sunset)
dt = datetime.now()
print(dt)

ten_pm = dt + timedelta(hours=1)

if sunset >= dt:
    setpin = digitalio.DigitalInOut(board.D5)
    setpin.direction = digitalio.Direction.OUTPUT
    setpin.value = True
    time.sleep(0.1)
    setpin.value = False
    sleep_seconds = sunset - dt
    print('sleeping until sunset: %s' % sleep_seconds)
    
elif ten_pm >= dt:
    unsetpin = digitalio.DigitalInOut(board.D6)
    unsetpin.direction = digitalio.Direction.OUTPUT
    unsetpin.value = True
    time.sleep(0.1)
    unsetpin.value = False
    sleep_seconds = ten_pm - dt
    print('sleeping until 10pm: %s' % sleep_seconds)
    
    
elif sunset <= dt:
    setpin = digitalio.DigitalInOut(board.D5)
    setpin.direction = digitalio.Direction.OUTPUT
    setpin.value = True
    time.sleep(0.1)
    setpin.value = False
    tomorrow = dt + timedelta(days=1)
    sleep_seconds = tomorrow.replace(hour=0, minute=0, second=0) - dt
    print('sleeping until midnight: %s' % sleep_seconds)
    
led.value = True
time.sleep(0.5)
led.value = False
led.direction = digitalio.Direction.INPUT
led.pull = Pull.DOWN

time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5 + sleep_seconds.total_seconds())
# Exit the program, and then deep sleep until the alarm wakes us.
alarm.exit_and_deep_sleep_until_alarms(time_alarm)