# GPS Tracking

This repo contains 3 components:

- Logger : Data acquisition and transmission using UDP
- UDP_Repeater : Centralisation of all the locations and redistribution to the clients
- Client : An instance connecting to the UDP_Repeater and generating both KML files and a video feed

## Requirements

### Logger

- cmake (optional)
- [gpsd, libgps](http://www.catb.org/gpsd/)

### UDP_Repeater

- Python2

### Client

- Python3

## Compilation

### Logger

Two options, cmake or by hand:

#### Cmake

    $ mkdir build
    $ cd build
    $ cmake ..
    $ make

#### Manually

    $ gcc -o logger logger.cpp -lgps -lm

## Example deployment

    $server        : hostname of the server hosting UDP_Repeater
    $serverUDPPort : UDP port on the server hosting UDP_Repeater receiving the data from the logger
    $serverTCPPort : TCP port on the server hosting UDP_Repeater receiving clients' TCP connections

### On all the machines that need to be tracked

Simply run the following command:

    $ ./logger $machineName $server 1234

With $machineName being MotoX, CarX, HeliX or PlaneX if you want a pretty icon in google earth.

### On the server

First, make sure that both $serverUDPPort and $serverTCPPort are accessible from outside. You do so
using netcat!

After checking, you can run the repeater by running the following command:

    $ ./udp_repeater.py $serverUDPPort $serverTCPPort

That should be all.

### On the machine(s) using the data to show on Google Earth or generating a livestream

Simply run client.py, as shown here:

    $ ./client.py $server $serverTCPPort

As new vehicles send their data, you should see more and more files in your home directory called 'Open_in_Google_Earth_RT_GPS_${machineName}.kml' and 'RT_GPS_${machineName}.kml'. Please open Google Earth and open all the files named 'Open_in_Google_Earth_RT_GPS_${machineName}.kml'. Google Earth will then poll on the second type of files to show the position of the vehicles. Congrats!
