#!/usr/bin/python
import Adafruit_DHT
from datetime import datetime as dt
from flask import Flask
import threading


app = Flask(__name__)

out = 'no data yet'
pin = 22


def getData():
    global out
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22 , pin)
    if humidity is not None and temperature is not None:
        out = dt.now().isoformat() + ' - Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
        print(out)
        with open('log.txt', 'a') as logFile:
            logFile.write(out + '\n')
        with open('log.csv', 'a') as logFile:
            logFile.write( dt.now().isoformat() + ',' + temperature + ',' + humidity + '\n' )
    else:
        print('Failed to get reading. Try again!')
        # sys.exit(1)
    threading.Timer(60, getData).start()


getData()


@app.route("/")
def hello():
    return out


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
