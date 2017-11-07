#!/usr/bin/env python
# coding: Latin-1

####################################################################
# This is the communications script for both Race Your Code robots #
#                                                                  #
# It is responsible for managing the threads which transmit and    #
# receive data during a race between the robots and the display    #
####################################################################

# Load all the library functions we want
import time
import math
import threading
import Globals
import Settings
import ImageProcessor
import SocketServer
import socket
import numpy
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
print 'Libraries loaded'

RAD_TO_DEG = 180.0 / math.pi
TYPE_STRING = type('')
TYPE_FLOAT = type(0.0)
TYPE_FLOAT64 = numpy.float64

# This function will be called when new data is received by the front robot
def NewDataFront():
	newData = Globals.dataReceived

# This function will be called when new data is received by the rear robot
def NewDataRear():
	newData = Globals.dataReceived
	# Copy the lights detection state from the front robot
	if newData.has_key('lights'):
		lights = int(newData['lights'])
		if lights != Globals.startLights:
			Globals.startLights = lights
			if lights == ImageProcessor.FIRST_GREEN:
				Globals.MonsterLed(0, 0.5, 0)
				ImageProcessor.LogData(ImageProcessor.LOG_MAJOR, 'Lights: 1 - Green')
			elif lights == ImageProcessor.SECOND_RED:
				Globals.MonsterLed(0.5, 0, 0)
				ImageProcessor.LogData(ImageProcessor.LOG_MAJOR, 'Lights: 2 - Red')
			elif lights == ImageProcessor.THIRD_GREEN_GO:
				Globals.MonsterLed(0, 1, 0)
				ImageProcessor.LogData(ImageProcessor.LOG_MAJOR, 'Lights: 3 - Green')
	# Check to see if the front robot has crossed the line yet
	if newData.has_key('lap-count'):
		lapCount = int(newData['lap-count'])
		if lapCount != Globals.lapCount:
			print '--- FRONT ROBOT CROSSED LINE ---'
			Globals.lapCount = lapCount
			Globals.lapTravelled = 0.0

# This function is called on both robots when about to transmit new data
def UpdateDataToSend():
	# Load new data
	if Globals.controller == None:
		Globals.dataToSend['track-position'] = '0'
		Globals.dataToSend['track-angle'] = '0'
		Globals.dataToSend['track-curve'] = '0'
		Globals.dataToSend['speed'] = '0'
		Globals.dataToSend['steering'] = '0'
	else:
		trackAngle = math.atan(Globals.controller.lastD1 / Settings.angleCorrection) * RAD_TO_DEG
		Globals.dataToSend['track-position'] = Globals.controller.lastD0
		Globals.dataToSend['track-angle'] = trackAngle
		Globals.dataToSend['track-curve'] = Globals.controller.lastD2
		Globals.dataToSend['speed'] = Globals.controller.lastSpeed
		Globals.dataToSend['steering'] = Globals.controller.lastSteering
	Globals.dataToSend['front'] = Globals.frontRobot
	Globals.dataToSend['target-lane'] = Globals.userTargetLane
	Globals.dataToSend['distance'] = Globals.lapTravelled
	Globals.dataToSend['lap-count'] = Globals.lapCount
	Globals.dataToSend['mode'] = Globals.imageMode
	Globals.dataToSend['lights'] = Globals.startLights
	Globals.dataToSend['track-found'] = Globals.trackFound
	Globals.dataToSend['user-1'] = ''
	Globals.dataToSend['user-2'] = ''
	Globals.dataToSend['user-3'] = ''

# Takes Globals.dataToSend and builds a transmission packet
def BuildDataPacket():
	packet = 'robot'
	# Add each key/value pair
	for key in Globals.dataToSend.keys():
		value = Globals.dataToSend[key]
		# Ensure values are strings
		if type(value) == TYPE_FLOAT64:
			value = '%+f' % (value)
		elif type(value) == TYPE_FLOAT:
			value = '%+f' % (value)
		elif type(value) != TYPE_STRING:
			value = str(value)
		if type(key) != TYPE_STRING:
			key = str(key)
		# Append the new entry
		packet += '|' + key + '=' + value
	return packet

# Class used to implement the incoming TCP server
class TcpServer(SocketServer.BaseRequestHandler):
	def handle(self):
		# Get the request data
		reqData = self.request.recv(2048)
		reqParts = reqData.split('|')
		command = reqParts[0].lower()
		# Handle incoming TCP command
		if command == 'robot':
			# Incoming update from the other robot, parse the data
			dataReceived = {}
			for i in range(1, len(reqParts)):
				lineParts = reqParts[i].lower().split('=')
				if len(lineParts) == 2:
					dataReceived[lineParts[0]] = lineParts[1]
			# Load into the global values
			Globals.dataReceived = dataReceived
			# Call the appropriate NewData callback
			if Globals.frontRobot:
				NewDataFront()
			else:
				NewDataRear()
		else:
			# Unexpected command
			print 'Unexpected command: %s' % (reqData)

# Thread for handling incoming data
class IncomingDataThread(threading.Thread):
	def __init__(self):
		super(IncomingDataThread, self).__init__()
		self.terminated = False
		self.tcpServer = SocketServer.TCPServer(("0.0.0.0", Settings.transferPort), TcpServer)
		self.tcpServer.timeout = 1
		ImageProcessor.LogData(ImageProcessor.LOG_CRITICAL, 'Incoming data thread started')
		self.start()
		
	def run(self):
		try:
			while not self.terminated:
				self.tcpServer.handle_request()
		except:
			print 'INCOMING-TCP-ERROR'
		ImageProcessor.LogData(ImageProcessor.LOG_CRITICAL, 'Incoming data thread terminated')

# Thread for sending updates
class OutgoingDataThread(threading.Thread):
	def __init__(self, targetIP):
		super(OutgoingDataThread, self).__init__()
		self.terminated = False
		self.targetIP = targetIP
		self.event = threading.Event()
		self.message = ''
		self.eventWait = 2.0 / Settings.frameRate
		ImageProcessor.LogData(ImageProcessor.LOG_CRITICAL, 'Outgoing data thread to %s started' % (self.targetIP))
		self.start()

	def run(self):
		while not self.terminated:
			self.event.wait(self.eventWait)
			if self.event.isSet():
				if self.terminated:
					break
				try:
					sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
					sender.connect((self.targetIP, Settings.transferPort))
					sender.settimeout(1)
					sender.sendto(self.message, (self.targetIP, Settings.transferPort))
					sender.close()
					del sender
				except:
					print 'OUTGOING-TCP-ERROR (%s)' % (self.targetIP)
				self.event.clear()
		ImageProcessor.LogData(ImageProcessor.LOG_CRITICAL, 'Outgoing data thread to %s terminated' % (self.targetIP))

# Decide which is our address and which is the other robot
if Globals.frontRobot:
	ourIP = Settings.ipFrontRobot
	theirIP = Settings.ipRearRobot
else:
	ourIP = Settings.ipRearRobot
	theirIP = Settings.ipFrontRobot

