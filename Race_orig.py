### Enable logging ###
#StartDetailedLoging()
#StartUserLog()

### Wait for the lights ###
WaitForGo()

### Racing until terminated ###
while Globals.running:
	# Wait until we reach the first corner
	WaitForWaypoint(2)
	# Wait until we reach the start / finish line
	WaitForWaypoint(1)

### Wait for a few seconds ###
#WaitForSeconds(4)

### Disable logging ###
EndDetailedLog()
EndUserLog()

### End of the race ###
FinishRace()
