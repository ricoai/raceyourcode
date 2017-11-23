#!/usr/bin/env python

import socket


BUFFER_SIZE = 1024

# Network addresses
ipDisplay = '192.168.1.216'			# IP address for the machine recording and displaying metrics
ipFrontRobot = 'RYC-Front'			# IP address for the front robot IP addresses
ipRearRobot = 'RYC-Rear'			# IP address for the front robot IP addresses
transferPort = 99					# Port number used when receiving updates from robots

#TCP_IP = ipFrontRobot
TCP_IP = '0.0.0.0'
TCP_PORT = transferPort

"""
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
"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
while True:
    conn, addr = s.accept()
    print 'Connection address:', addr

    data = conn.recv(BUFFER_SIZE)
    if not data:
        print "NO MORE DATA"
        break
    #print "received data:", data
    items = data.split('|')
    for item in items:
        print item
    print "-----------------------------------------"

    #conn.send(data)  # echo
conn.close()