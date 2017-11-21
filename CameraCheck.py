#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import time
import os
import sys
import io
import threading
import cv2
import numpy
import Settings
print 'Libraries loaded'

# Global values
global running
global capture
global frameTimes
global frameLock
global processorPool
global frameAnnounce
global frameCounter
global displayFrame
frameCounter = 0
frameAnnounce = 0
running = True
frameTimes = []
frameLock = threading.Lock()
processorPool = []
displayFrame = None

# Filming parameters
filePattern = './%s/%010d.jpg'
processingThreads = 1
frameRate = 5 #20
imageScale = 5.0
imageWidth  = int(Settings.imageWidth * imageScale)
imageHeight = int(Settings.imageHeight * imageScale)
fpsInterval = frameRate # Once per second (if running well)
scaleFinalImage = 1.0
showFps = True

# Lights box
lightsX1 = int(Settings.lightsX1 * imageScale)
lightsX2 = int(Settings.lightsX2 * imageScale)
lightsY1 = int(Settings.lightsY1 * imageScale)
lightsY2 = int(Settings.lightsY2 * imageScale)
lightsBorder = 3
lightsBorderColour = (255, 0, 255)

# Start box
startX1 = int(Settings.startX1 * imageScale)
startX2 = int(Settings.startX2 * imageScale)
startY1 = int((Settings.startY - 1) * imageScale)
startY2 = int((Settings.startY + 1) * imageScale)
startBorder = 3
startBorderColour = (255, 255, 0)

# Track box
trackX1 = int(Settings.cropX1 * imageScale)
trackX2 = int(Settings.cropX2 * imageScale)
trackY1 = int(Settings.cropY1 * imageScale)
trackY2 = int(Settings.cropY2 * imageScale)
trackBorder = 3
trackBorderColour = (0, 255, 255)

# Image stream processing thread
class StreamProcessor(threading.Thread):
	def __init__(self, name):
		super(StreamProcessor, self).__init__()
		self.event = threading.Event()
		self.terminated = False
		self.name = str(name)
		self.shownCount = 0
		self.eventWait = (2.0 * processingThreads) / frameRate
		print 'Processor thread %s started with idle time of %.2fs' % (self.name, self.eventWait)
		self.start()

	def run(self):
		# This method runs in a separate thread
		while not self.terminated:
			# Wait for an image to be written to the stream
			if self.event.wait(self.eventWait):
				if self.terminated:
					break
				try:
					# grab the image and do some processing on it
					image = self.nextFrame
					self.ProcessImage(image)
				finally:
					# Reset the event
					self.nextFrame = None
					self.event.clear()
					# Return ourselves to the pool at the back
					with frameLock:
						processorPool.insert(0, self)
		print 'Processor thread %s terminated' % (self.name)
	
	# Image processing function
	def ProcessImage(self, image):
		# Frame rate counter
		global lastFrameStamp
		global frameAnnounce
		global frameCounter
		global displayFrame
		with frameLock:
			self.frame = frameCounter
			frameAnnounce += 1
			frameCounter += 1
			if frameAnnounce == fpsInterval:
				frameStamp = time.time()
				if showFps:
					fps = fpsInterval / (frameStamp - lastFrameStamp)
					fps = '%.1f FPS - %d total frames' % (fps, frameCounter)
					print fps
				frameAnnounce = 0
				lastFrameStamp = frameStamp
			else:
				pass
		if Settings.flippedImage:
			image = cv2.flip(image, -1)
		displayImage = image
		# Draw bounding boxes
		cv2.rectangle(displayImage, (lightsX1, lightsY1), (lightsX2, lightsY2), lightsBorderColour, lightsBorder, lineType = cv2.CV_AA)
		cv2.rectangle(displayImage, (startX1, startY1), (startX2, startY2), startBorderColour, startBorder, lineType = cv2.CV_AA)
		cv2.rectangle(displayImage, (trackX1, trackY1), (trackX2, trackY2), trackBorderColour, trackBorder, lineType = cv2.CV_AA)
		# Center line
		centerX = int(imageWidth * 0.5)
		cv2.line(displayImage, (centerX, 0), (centerX, imageHeight), (0, 127, 255), 3, lineType = cv2.CV_AA)
		displayFrame = displayImage

# Image capture thread
class ImageCapture(threading.Thread):
	def __init__(self):
		super(ImageCapture, self).__init__()
		self.start()

	# Stream delegation loop
	def run(self):
		global running
		global capture
		while running:
			# Grab the oldest unused processor thread
			with frameLock:
				if processorPool:
					processor = processorPool.pop()
				else:
					processor = None
			if processor:
				# Grab the next frame and send it to the processor
				ret, frame = capture.read()
				if ret:
					processor.nextFrame = frame
					processor.event.set()
				else:
					print 'Capture stream lost...'
					running = False
					break
			else:
				# When the pool is starved we wait a while to allow a processor to finish
				time.sleep(0.01)
		print 'Streaming terminated.'

global lastFrameStamp
lastFrameStamp = time.time()

# Startup sequence
print 'Setup camera'
os.system('sudo modprobe bcm2835-v4l2')
capture = cv2.VideoCapture(0) 
capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, imageWidth);
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, imageHeight);
capture.set(cv2.cv.CV_CAP_PROP_FPS, frameRate);
if not capture.isOpened():
	capture.open()
	if not capture.isOpened():
		print 'Failed to open the camera'
		sys.exit()

print 'Setup stream processor threads'
processorPool = [StreamProcessor(i+1) for i in range(processingThreads)]
allProcessors = processorPool[:]

print 'Wait ...'
time.sleep(2)
captureThread = ImageCapture()

try:
	print 'Press CTRL+C to quit'
	# Loop indefinitely
	while running:
		# See if there is a frame to show
		if displayFrame != None:
			# Show the next frame
			if scaleFinalImage != 1.0:
				size = (int(displayFrame.shape[1] * scaleFinalImage), int(displayFrame.shape[0] * scaleFinalImage))
				displayFrame = cv2.resize(displayFrame, size, interpolation = cv2.INTER_CUBIC)
			cv2.imshow('Camera', displayFrame)
			cv2.waitKey(100)
		else:
			# Wait for the interval period
			time.sleep(0.1)
except KeyboardInterrupt:
	# CTRL+C exit, disable all drives
	print '\nUser shutdown'
except:
	# Unexpected error, shut down!
	e = sys.exc_info()[0]
	print
	print e
	print '\nUnexpected error, shutting down!'
# Tell each thread to stop, and wait for them to end
running = False
while allProcessors:
	with frameLock:
		processor = allProcessors.pop()
	processor.terminated = True
	processor.event.set()
	processor.join()
captureThread.join()
capture.release()
del capture
print 'Program terminated.'
