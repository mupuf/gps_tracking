#!/usr/bin/env python2

from socket import *
import SocketServer
import threading
import sys

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

        print data

        tcpClientsMutex.acquire()
        for client in tcpClients:
            try:
                client.send(data + "\n")
            except:
                print ("A client got disconnected")
                tcpClients.remove(client)
        tcpClientsMutex.release()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: {} udp_port tcp_port".format(sys.argv[0])
        sys.exit(1)

    tcpClients = []
    tcpClientsMutex = threading.Lock()

    # Set up the UDP server
    HOST, PORT = "0.0.0.0", int(sys.argv[1])
    print ("Setting up the UDP server on {}:{}".format(HOST,PORT))
    server = SocketServer.UDPServer((HOST, PORT), UDPHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Set up the TCP server
    HOST, PORT = "0.0.0.0", int(sys.argv[2])
    print ("Setting up the TCP server on {}:{}".format(HOST,PORT))
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind((HOST, PORT))
    serversock.listen(5)

    while 1:
        clientsock, addr = serversock.accept()
        print 'New connection from: ', addr

        tcpClientsMutex.acquire()
        tcpClients.append(clientsock)
        tcpClientsMutex.release()
