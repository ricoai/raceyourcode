speed_val = 100

### Start of the race ###
# Wait until we can see the track
while not TrackFound():
	WaitForSeconds(1.0)
# We can see the track now, start by following the lane we are on
#trackLane = round(CurrentTrackPosition())
#AimForLane(trackLane)
# Save a start-line image
photo = GetLatestImage()
SaveImage(photo, 'Start-line')
# Start logging what happens
StartUserLog()
#StartDetailedLog()
# Wait for the go signal from the start/stop lights.
WaitForGo()
# Go at max speed
Speed(speed_val)

### During the race ###
# Race until terminated
while Globals.running:
	# Full speed to the first corner
	Speed(speed_val)
	AimForLane(1.5)
	WaitForWaypoint(2)
	# Slow down, move to the inside in stages and wait for the apex
	AimForLane(1.0)
	WaitForWaypoint(3)
	# Speed up and move to the center until the S curve start
	AimForLane(1.0)
	WaitForWaypoint(4)
	Speed(95)
	# Move towards the outside until the S curve changes
	AimForLane(1.0)
	WaitForWaypoint(5)
	#Speed(70)
	# Move towards the inside until the S curve ends
	AimForLane(0.5)
	WaitForWaypoint(6)
	# Slow down and move to the inside around the corner
	Speed(90)
	AimForLane(1.5)
	WaitForWaypoint(7)
	# Speed up for the back straight along the center
	Speed(speed_val)
	AimForLane(0.0)
	WaitForWaypoint(8)
	# High speed for the last corner on the inside
	Speed(speed_val)
	AimForLane(1.0)
	WaitForWaypoint(9)
	# Full speed until the start/finish line along the outside
	Speed(speed_val)
	AimForLane(0.0)
	WaitForWaypoint(1)

### End of the race ###
# Save a finish-line image
photo = GetLatestImage()
SaveImage(photo, 'Finished')
# Slow the MonsterBorg down gradually from 100% to 0%
for slowing in range(99, -1, -1):
	Speed(slowing)
	WaitForSeconds(0.01)
# Stop the logging
EndUserLog()
EndDetailedLog()
# End the race (will stop the robot and end the program)
FinishRace()
