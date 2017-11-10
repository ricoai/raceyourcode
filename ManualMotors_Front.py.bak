#!/usr/bin/env python
# coding: latin-1

# Import library functions we need 
import ThunderBorg
import Tkinter
import sys

# Setup the ThunderBorg
global TB
TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
#TB.i2cAddress = 0x15           # Uncomment and change the value if you have changed the board address
TB.Init()                       # Set the board up (checks the board is connected)
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print 'No ThunderBorg found, check you are attached :)'
    else:
        print 'No ThunderBorg at address %02X, but we did find boards:' % (TB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
        print 'TB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()

# Class representing the GUI dialog
class ThunderBorg_tk(Tkinter.Tk):
    # Constructor (called when the object is first created)
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.OnExit) # Call the OnExit function when user closes the dialog
        self.Initialise()

    # Initialise the dialog
    def Initialise(self):
        global TB
        self.title('Manual motor control')
        # Setup a grid of 2 sliders which command each motor output, plus a stop button for both motors
        self.grid()
        self.lblSpeed = Tkinter.Label(self, text = 'Speed', justify = Tkinter.CENTER, bg = '#000', fg = '#0F0')
        self.lblSpeed['font'] = ('Trebuchet', 20, 'bold')
        self.lblSpeed.grid(column = 0, row = 0, rowspan = 1, columnspan = 2, sticky = 'NSEW')
        self.sldSpeed = Tkinter.Scale(self, from_ = +100, to = -100, orient = Tkinter.VERTICAL, command = self.sldSpeed_move)
        self.sldSpeed.set(0)
        self.sldSpeed.grid(column = 0, row = 1, rowspan = 1, columnspan = 1, sticky = 'NS')
        self.lblSteering = Tkinter.Label(self, text = 'Steering', justify = Tkinter.CENTER, bg = '#000', fg = '#0F0')
        self.lblSteering['font'] = ('Trebuchet', 20, 'bold')
        self.lblSteering.grid(column = 0, row = 2, rowspan = 1, columnspan = 2, sticky = 'NSEW')
        self.sldSteering = Tkinter.Scale(self, from_ = -100, to = +100, orient = Tkinter.HORIZONTAL, command = self.sldSteering_move)
        self.sldSteering.set(0)
        self.sldSteering.grid(column = 0, row = 3, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.butOff = Tkinter.Button(self, text = 'All Off', command = self.butOff_click)
        self.butOff['font'] = ("Arial", 20, "bold")
        self.butOff.grid(column = 0, row = 4, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 4)
        self.grid_rowconfigure(2, weight = 1)
        self.grid_rowconfigure(3, weight = 1)
        self.grid_rowconfigure(4, weight = 1)
        # Set the size of the dialog
        self.resizable(True, True)
        self.geometry('400x600')
        # Setup the initial motor state
        TB.MotorsOff()

    # Set the motor speeds from speed and steering levels
    def SetDrive(self, speed, steering):
        global TB
        driveLeft = speed
        driveRight = speed
        if steering < -0.01:
            # Turning left
            driveLeft *= 1.0 + steering
        elif steering > 0.01:
            # Turning right
            driveRight *= 1.0 - steering
        TB.SetMotor1(driveRight) # Right motors
        TB.SetMotor2(driveLeft)  # Left motors

    # Called when the user closes the dialog
    def OnExit(self):
        global TB
        # Turn drives off and end the program
        TB.MotorsOff()
        self.quit()
  
    # Called when sldSpeed is moved
    def sldSpeed_move(self, value):
        speed = float(value) / 100.0
        steering = float(self.sldSteering.get()) / 100.0
        self.SetDrive(speed, steering)

    # Called when sldSteering is moved
    def sldSteering_move(self, value):
        speed = float(self.sldSpeed.get()) / 100.0
        steering = float(value) / 100.0
        self.SetDrive(speed, steering)

    # Called when butOff is clicked
    def butOff_click(self):
        global TB
        TB.MotorsOff()
        self.sldSpeed.set(0)
        self.sldSteering.set(0)

# if we are the main program (python was passed a script) load the dialog automatically
if __name__ == "__main__":
    app = ThunderBorg_tk(None)
    app.mainloop()

