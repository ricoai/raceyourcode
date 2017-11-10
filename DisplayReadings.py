#!/usr/bin/env python
# coding: latin-1

# Import library functions we need 
import tkinter
import sys
import threading
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Settings
dataPort = 99
displayWidth = 12

# Storage for robot status
global robotFront
global robotRear
robotFront = {
        'front':'front',
        'speed':'speed',
        'steering':'steering',
        'target-lane':'target-lane',
        'distance':'distance',
        'lap-count':'lap-count',
        'mode':'mode',
        'lights':'lights',
        'track-found':'track-found',
        'track-position':'track-pos',
        'track-angle':'track-angle',
        'track-curve':'track-curve',
        'user-1':'user-1',
        'user-2':'user-2',
        'user-3':'user-3',
}
robotRear = {
        'front':'front',
        'speed':'speed',
        'steering':'steering',
        'target-lane':'target-lane',
        'distance':'distance',
        'lap-count':'lap-count',
        'mode':'mode',
        'lights':'lights',
        'track-found':'track-found',
        'track-position':'track-pos',
        'track-angle':'track-angle',
        'track-curve':'track-curve',
        'user-1':'user-1',
        'user-2':'user-2',
        'user-3':'user-3',
}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle MJPEG requests in their own thread"""

# Thread for handling HTTP requests
class ServerThread(threading.Thread):
    def __init__(self):
        super(ServerThread, self).__init__()
        self.httpServer = ThreadedHTTPServer(('', mjpegPort), MjpegHandler)
        
    def run(self):
        try:
            self.httpServer.serve_forever()
        except:
            print('--')

# Class used to implement the TCP server
class TcpServer(socketserver.BaseRequestHandler):
    def handle(self):
        global robotFront
        global robotRear
        # Get the request data
        reqData = self.request.recv(1024).strip()
        reqParts = reqData.split('|')
        command = reqParts[0].upper()
        # Handle incoming TCP command
        if command == 'ROBOT':
            # Robot status update
            dataReceived = {}
            for i in range(1, len(reqParts)):
                lineParts = reqParts[i].lower().split('=')
                if len(lineParts) == 2:
                    dataReceived[lineParts[0]] = lineParts[1]
            if 'front' in dataReceived:
                if dataReceived['front'].lower().strip() == 'true':
                    # Front robot data
                    targetRobot = robotFront
                else:
                    # Rear robot data
                    targetRobot = robotRear
                # Copy over updates (allows for partial updates)
                for key in list(dataReceived.keys()):
                    targetRobot[key] = dataReceived[key]
            else:
                print('Robot data received, no front flag...')
        else:
            # Unexpected command
            print('Unexpected command: %s' % (command))
            dataReceived = {}
            for i in range(1, len(reqParts)):
                lineParts = reqParts[i].lower().split('=')
                if len(lineParts) == 2:
                    print('    %s = %s' % (lineParts[0], lineParts[1]))
                else:
                    print('    ? %s' % (reqParts[i]))

# Thread for handling incoming data
class DataThread(threading.Thread):
    def __init__(self):
        super(DataThread, self).__init__()
        self.terminated = False
        try:
            self.tcpServer = socketserver.TCPServer(("0.0.0.0", dataPort), TcpServer)
        except:
            # Failed to open the port, report common issues
            print()
            print('Failed to open port %d' % (dataPort))
            print('Make sure you are running this script with gksudo permissions on Linux')
            print('Other problems include running another script with the same port')
            print('If the script was just working recently try waiting a minute first')
            print() 
            # Flag the script to exit
            sys.exit(1)
        self.tcpServer.timeout = 1
        
    def run(self):
        try:
            while not self.terminated:
                self.tcpServer.handle_request()
        except:
            print('TCP-ERROR')

# Class representing the GUI dialog
class Status_tk(tkinter.Tk):
    # Constructor (called when the object is first created)
    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.OnExit) # Call the OnExit function when user closes the dialog
        self.Initialise()

    # Initialise the dialog
    def Initialise(self):
        self.title('Robot status display')
        # Setup a grid labels for showing robot status
        self.grid()
        self.lblFront = tkinter.Label(self, text = 'Front robot', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront['font'] = ('Trebuchet', 20, 'bold')
        self.lblFront.grid(column = 0, row = 0, rowspan = 1, columnspan = 2, sticky = 'NSEW')
        self.lblFront0a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront0a['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront0a.grid(column = 0, row = 1, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront0b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront0b['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront0b.grid(column = 1, row = 1, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront1a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront1a['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront1a.grid(column = 0, row = 2, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront1b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront1b['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront1b.grid(column = 1, row = 2, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront2a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront2a['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront2a.grid(column = 0, row = 3, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront2b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront2b['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront2b.grid(column = 1, row = 3, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront3a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront3a['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront3a.grid(column = 0, row = 4, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront3b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront3b['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront3b.grid(column = 1, row = 4, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront4a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront4a['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront4a.grid(column = 0, row = 5, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront4b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront4b['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront4b.grid(column = 1, row = 5, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront5a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront5a['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront5a.grid(column = 0, row = 6, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront5b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront5b['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront5b.grid(column = 1, row = 6, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront6a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront6a['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront6a.grid(column = 0, row = 7, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblFront6b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#FF0')
        self.lblFront6b['font'] = ('Trebuchet', 14, 'bold')
        self.lblFront6b.grid(column = 1, row = 7, rowspan = 1, columnspan = 1, sticky = 'NSEW')

        self.lblRear = tkinter.Label(self, text = 'Rear robot', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear['font'] = ('Trebuchet', 20, 'bold')
        self.lblRear.grid(column = 2, row = 0, rowspan = 1, columnspan = 2, sticky = 'NSEW')
        self.lblRear0a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear0a['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear0a.grid(column = 2, row = 1, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear0b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear0b['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear0b.grid(column = 3, row = 1, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear1a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear1a['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear1a.grid(column = 2, row = 2, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear1b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear1b['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear1b.grid(column = 3, row = 2, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear2a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear2a['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear2a.grid(column = 2, row = 3, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear2b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear2b['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear2b.grid(column = 3, row = 3, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear3a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear3a['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear3a.grid(column = 2, row = 4, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear3b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear3b['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear3b.grid(column = 3, row = 4, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear4a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear4a['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear4a.grid(column = 2, row = 5, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear4b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear4b['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear4b.grid(column = 3, row = 5, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear5a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear5a['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear5a.grid(column = 2, row = 6, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear5b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear5b['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear5b.grid(column = 3, row = 6, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear6a = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear6a['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear6a.grid(column = 2, row = 7, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.lblRear6b = tkinter.Label(self, text = '?', justify = tkinter.CENTER, bg = '#000', fg = '#0FF')
        self.lblRear6b['font'] = ('Trebuchet', 14, 'bold')
        self.lblRear6b.grid(column = 3, row = 7, rowspan = 1, columnspan = 1, sticky = 'NSEW')

        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)
        self.grid_columnconfigure(3, weight = 1)
        self.grid_rowconfigure(0, weight = 2)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_rowconfigure(2, weight = 1)
        self.grid_rowconfigure(3, weight = 1)
        self.grid_rowconfigure(4, weight = 1)
        self.grid_rowconfigure(5, weight = 1)
        self.grid_rowconfigure(6, weight = 1)
        self.grid_rowconfigure(7, weight = 1)
        # Set the size of the dialog
        self.resizable(True, True)
        self.geometry('800x400')
        # Start polling
        self.after(1, self.Poll)

    # Helper function for text display
    def getValue(self, values, shownKey, width):
        if shownKey in values:
            value = values[shownKey]
        else:
            value = '?'
        return value[:width]

    # Polling function
    def Poll(self):
        global robotFront
        global robotRear

        # Update the front robot status
        self.lblFront0a['text'] = self.getValue(robotFront, 'steering', displayWidth)
        self.lblFront0b['text'] = self.getValue(robotFront, 'speed', displayWidth)
        self.lblFront1a['text'] = self.getValue(robotFront, 'target-lane', displayWidth)
        self.lblFront1b['text'] = self.getValue(robotFront, 'lap-count', displayWidth)
        self.lblFront2a['text'] = self.getValue(robotFront, 'mode', displayWidth)
        self.lblFront2b['text'] = self.getValue(robotFront, 'lights', displayWidth)
        self.lblFront3a['text'] = self.getValue(robotFront, 'track-found', displayWidth)
        self.lblFront3b['text'] = self.getValue(robotFront, 'track-position', displayWidth)
        self.lblFront4a['text'] = self.getValue(robotFront, 'track-angle', displayWidth)
        self.lblFront4b['text'] = self.getValue(robotFront, 'track-curve', displayWidth)
        self.lblFront5a['text'] = self.getValue(robotFront, 'distance', displayWidth)
        self.lblFront5b['text'] = self.getValue(robotFront, 'user-1', displayWidth)
        self.lblFront6a['text'] = self.getValue(robotFront, 'user-2', displayWidth)
        self.lblFront6b['text'] = self.getValue(robotFront, 'user-3', displayWidth)

        # Update the rear robot status
        self.lblRear0a['text'] = self.getValue(robotRear, 'steering', displayWidth)
        self.lblRear0b['text'] = self.getValue(robotRear, 'speed', displayWidth)
        self.lblRear1a['text'] = self.getValue(robotRear, 'target-lane', displayWidth)
        self.lblRear1b['text'] = self.getValue(robotRear, 'lap-count', displayWidth)
        self.lblRear2a['text'] = self.getValue(robotRear, 'mode', displayWidth)
        self.lblRear2b['text'] = self.getValue(robotRear, 'lights', displayWidth)
        self.lblRear3a['text'] = self.getValue(robotRear, 'track-found', displayWidth)
        self.lblRear3b['text'] = self.getValue(robotRear, 'track-position', displayWidth)
        self.lblRear4a['text'] = self.getValue(robotRear, 'track-angle', displayWidth)
        self.lblRear4b['text'] = self.getValue(robotRear, 'track-curve', displayWidth)
        self.lblRear5a['text'] = self.getValue(robotRear, 'distance', displayWidth)
        self.lblRear5b['text'] = self.getValue(robotRear, 'user-1', displayWidth)
        self.lblRear6a['text'] = self.getValue(robotRear, 'user-2', displayWidth)
        self.lblRear6b['text'] = self.getValue(robotRear, 'user-3', displayWidth)

        # Re-run the poll after 100 ms
        self.after(100, self.Poll)

    # Called when the user closes the dialog
    def OnExit(self):
        # End the program
        self.quit()

# if we are the main program (python was passed a script) load the dialog automatically
if __name__ == "__main__":
    dataReceiver = DataThread()
    dataReceiver.start()
    try:
        app = Status_tk(None)
        app.mainloop()
    finally:
        dataReceiver.terminated = True
        dataReceiver.tcpServer.socket.close()
        dataReceiver.join()

