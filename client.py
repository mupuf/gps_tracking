#!/usr/bin/env python3
from socket import *
from os.path import expanduser
from time import ctime, gmtime, strftime
import sys

class Event:
    def __init__(self, eventLine):
        eventLine = eventLine.strip('\n')
        fields = eventLine.split('\t')
        print (fields)
        self.nodeName = fields[0]
        self.timestamp = int(fields[1])
        self.distance = float(fields[2])
        self.latitude = float(fields[3])
        self.longitude = float(fields[4])
        self.altitude = float(fields[5])
        self.speed = float(fields[6])

def writeStringToFile(filepath, string):
    with open(filepath, 'w') as f:
        f.write(string)
        f.close()

def createGoogleEarthHelper(nodeName, kmlFilePath):
    return '''\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<NetworkLink>
	<name>Realtime GPS for {nodeName}</name>
	<open>1</open>
	<Link>
		<href>{kmlFilePath}</href>
		<refreshMode>onInterval</refreshMode>
		<refreshInterval>1</refreshInterval>
	</Link>
</NetworkLink>
</kml>
'''.format(nodeName=nodeName, kmlFilePath=kmlFilePath)

def findIcon(event):
    if event.nodeName.lower().startswith("moto"):
        return "http://maps.google.com/mapfiles/kml/shapes/motorcycling.png"
    if event.nodeName.lower().startswith("car"):
        return "http://maps.google.com/mapfiles/kml/shapes/cabs.png"
    if event.nodeName.lower().startswith("heli"):
        return "http://maps.google.com/mapfiles/kml/shapes/heliport.png"
    if event.nodeName.lower().startswith("plane"):
        return "http://maps.google.com/mapfiles/kml/shapes/airports.png"
    return "http://maps.google.com/mapfiles/kml/paddle/red-stars.png"

def kmlize(event):
    '''http://code.google.com/apis/kml/documentation/kmlreference.html
       for official kml document'''
    return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
<Document>
    <Style id="highlightPlacemark">
        <IconStyle>
            <Icon>
                <href>{iconUrl}</href>
            </Icon>
        </IconStyle>
    </Style>
    <Placemark>
        <name>{nodeName} ({speed} km/h)</name>
        <description>Last updated: {date}<br/>Altitude: {altitude} m</description>
        <styleUrl>#highlightPlacemark</styleUrl>
        <Point>
            <coordinates>{longitude}, {latitude},0</coordinates>
        </Point>
    </Placemark>
</Document>
</kml>""".format(nodeName=event.nodeName, longitude=event.longitude,
		 latitude=event.latitude, altitude=event.altitude,
		 speed=event.speed, date=strftime("%Y-%m-%d %H:%M:%S", gmtime()),
		 iconUrl=findIcon(event))

def updateLocationGoogleEarth(event):
    directory = expanduser("~") + "/";
    kmlFilePath = directory + "RT_GPS_" + event.nodeName + ".kml"
    helperFileName = directory + "Open_in_Google_Earth_RT_GPS_" + event.nodeName + ".kml"

    writeStringToFile(helperFileName, createGoogleEarthHelper(event.nodeName, kmlFilePath))
    writeStringToFile(kmlFilePath, kmlize(event))

def generateNewImage(event):
    try:
        if event.distance < generateNewImage.maxDistance:
            return
    except AttributeError:
        pass
    generateNewImage.maxDistance = event.distance

    # Do stuff here!
    

if __name__=='__main__':
    if len(sys.argv) != 3:
        print ("Usage: {} host port".format(sys.argv[0]))
        sys.exit(1)
    
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)

    file = tcpCliSock.makefile('r')

    while True:
        event = Event(file.readline())
        updateLocationGoogleEarth(event)
        generateNewImage(event)

    tcpCliSock.close()