#!/usr/bin/python
import Adafruit_DHT
from datetime import datetime as dt
from flask import Flask
import threading
import pygal
import csv

app = Flask(__name__)

out = 'no data yet'
pin = 22

dataLen = 50
updateTimer = 60*30

## Read saved dara on startup
temperatureData = []
humidityData = []
dateData = []



with open('log.csv') as csvFile:
    bla = csv.reader(csvFile)
    for row in bla:
        temperatureData.append(float(row[1]))
        humidityData.append(float(row[2]))
        dateData.append(row[0])
        if len(temperatureData) > dataLen:
            temperatureData.pop(0)
            humidityData.pop(0)
            dateData.pop(0)


def updateChart(d,t,h):
    lineChart = pygal.Line(interpolate='cubic')
    lineChart.title = 'Messungen'
    lineChart.x_labels = dateData
    lineChart.add('Temperatur', temperatureData)
    lineChart.add('Luft', humidityData)
    return lineChart.render_data_uri()


def getData():
    global out, temperatureData, dateData, humidityData, lineChartRendered
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22 , pin)
    if humidity is not None and temperature is not None:
        temperatureData.append(temperature)
        humidityData.append(humidity)
        dateData.append(dt.now().isoformat())
        lineChartRendered = updateChart(dateData[-dataLen:], temperatureData[-dataLen:], humidityData[-dataLen:])
        out = dt.now().isoformat() + ' - Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
        print(out)
        with open('log.txt', 'a') as logFile:
            logFile.write(out + '\n')
        with open('log.csv', 'a') as logFile:
            logFile.write( dt.now().isoformat() + ',' + str(temperature) + ',' + str(humidity) + '\n' )
    else:
        print('Failed to get reading. Try again!')
        # sys.exit(1)
    threading.Timer(updateTimer, getData).start()


getData()


@app.route("/")
def hello():
    html = '''
        <!DOCTYPE html>
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
            </head>
            <body>
                <h1>%s</h1>
                <embed type="image/svg+xml" src='%s'></img>
                <h3>DOWNLOAD</h3>
                <a href='/svg' download="messung.svg">Diagramm (SVG)</a><br>
                <a href='/txt' download="messung.txt">Text-Datei</a><br>
                <a href='/svg' download="messung.csv">CSV (Excel, etc.)</a><br>
            </body>
        </html>
    ''' % (out , lineChartRendered)
    return html



@app.route("/csv")
def getCSV():
    csv = ''
    for i in range(len(temperatureData)):
        csv += dateData[i] + ',' + str(temperatureData[i]) + ',' + str(humidityData[i]) + '\n'
    return csv



@app.route("/svg")
def getSVG():
    return updateChart(dateData, temperatureData, humidityData)



@app.route("/txt")
def getTXT():
    txt = ''
    for i in range(len(temperatureData)):
        d = dateData[i]
        txt += d[8:10] + '.' + d[5:7] + '.' + d[:4] +' -- ' + d[11:16] + ' // Temperatur={0:0.1f}*  Luftfeuchtigkeit={1:0.1f}%'.format(temperatureData[i], humidityData[i]) + '\n'
    return txt



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
