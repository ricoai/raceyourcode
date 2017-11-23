#!/usr/bin/env python

import socket


BUFFER_SIZE = 1024

# Network addresses
ipDisplay = '192.168.1.216'			# IP address for the machine recording and displaying metrics
ipFrontRobot = 'RYC-Front'			# IP address for the front robot IP addresses
ipRearRobot = 'RYC-Rear'			# IP address for the front robot IP addresses
transferPort = 99					# Port number used when receiving updates from robots

TCP_IP = ipDisplay
TCP_PORT = transferPort


data = ""
try:
    sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sender.connect((TCP_IP, TCP_PORT))
    sender.settimeout(1)
    while True:
        data = sender.recv(BUFFER_SIZE)
        print "received data:", data
    sender.close()
except Exception as ex:
    print "Error connecting", ex

