# Play Note Function
# Eventually a Play melody function that takes in a list of notes
# 	 Time delays between each note that is determined by a tempo variable
#	 Metronome will affect a delay between notes played
# Map functions that mess with that list
# 	 Would be cool to map a dynamics list as well
# We could have a make scale function
# Randomize rhythm function that changes the placement of "-1"
# Modify Melody function that may slightly change some of the notes
# 	 Could include a scale feature so that they are checked if they are in the scale
# Loop function that repeats whatever melodies are provided to it
# Convert to Major or Minor Function could work if all the notes come from a certain scale
# Determine Key function could predict what key a melody is given the notes

import argparse
import random
from pythonosc import osc_message_builder
from pythonosc import udp_client
from time import sleep
import math

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=7123, help="The port the OSC server is listening on")
args = parser.parse_args()
client = udp_client.UDPClient(args.ip, args.port)

TEMPO = 120 # Global tempo variable, determines playback of a line

def setTempo(tempo):
	global TEMPO
	TEMPO = tempo
	return TEMPO

# ---------------------Helper Functions---------------------

# Takes a tempo and the note's duration and calculates exact milliseconds
# Current calculations are assuming 4/4 I think...
def calculateNoteDuration(noteLength):
	global TEMPO
	durationDict = {"whole": 1, "half": 2, "quarter": 4, "eighth": 8, "sixteenth": 16}

	millisecondsPerMeasure = (4/TEMPO) * 60 * 1000
	
	try:
		noteDuration = durationDict[noteLength]
		return millisecondsPerMeasure/noteDuration
	except:
		print("Invalid note length included: Using quarter notes")
		return millisecondsPerMeasure/4

# generates a random float between 0 and 127
def randomMIDIVal():
	return random.random() * 127.

# Convert a frequency to a midi value
def fToM(frequency):
	return 12 * math.log2(frequency/440) + 69

# Convert a midi value to a frequency
def mToF(midiVal):
	return 440 * math.pow(2, (midiVal - 69)/12)


# ---------------------Make Sounds---------------------

# Sends an OSC Message to Max to play a note via noteout
# MIDI note value required, other parameters optional
# Currently, notes last full duration
# 	Could consider adding a staccato/legato parameter
def playNote(midiVal, velocity=60, duration=1000, instrument=0):
	if midiVal != -1:
		msg = osc_message_builder.OscMessageBuilder(address = "/playNote")
		msg.add_arg(midiVal)
		msg.add_arg(velocity)
		msg.add_arg(duration)
		msg.add_arg(instrument)
		msg = msg.build()
		client.send(msg)
	sleep(duration/1000)

# Input is a list of notes
# -1 will play a rest since 0 technically represents C
# The speed of playback is determined by the TEMPO variable
# Velocity can be a number or a list (even rests have velocities)
def playLine(midiLine, noteLength="quarter", velocity=60, instrument=0):
	if type(midiLine) != list:
		print("The playLine function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	duration = calculateNoteDuration(noteLength)

	if type(velocity) == int or type(velocity) == float:
		[playNote(midiVal, velocity, duration, instrument) for midiVal in midiLine]
	elif type(velocity) == list:
		if len(midiLine) == len(velocity):
			[playNote(midiVal, velocityVal, duration, instrument) for midiVal, velocityVal in zip(midiLine, velocity)]
		else:
			print("Velocity list is not the same length as the MIDI note list: Playing with velocity of 60")
			[playNote(midiVal, 60, duration, instrument) for midiVal in midiLine]


# ---------------------Map Functions---------------------

# Will transpose a list of midinotes, the number of steps provided
def transpose(midiLine, numSteps):
	if type(midiLine) != list:
		print("The transpose function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	return list(map((lambda midiNote: midiNote + numSteps), midiLine))

# changes placement of all pitches and rests 
def shuffleLine(midiLine):
	if type(midiLine) != list:
		print("The shuffleLine function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return
	copy = list(midiLine)
	random.shuffle(copy)
	return copy

# Changes pitches, maintains rhythm
def shufflePitches(midiLine):
	if type(midiLine) != list:
		print("The shufflePitches function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	# remove all the rests and shuffle the order of the pitches
	filteredLine = shuffleLine(list(filter((lambda nonRest: nonRest != -1), midiLine)))
	newLine = []
	
	for note in midiLine:
		if note != -1:
			newLine.append(filteredLine.pop())
		else:
			newLine.append(-1)

	return newLine

# Changes rhythm, maintains pitches
def shuffleRests(midiLine):
	if type(midiLine) != list:
		print("The shuffleRests function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	# remove all the rests
	filteredLine = list(filter((lambda nonRest: nonRest != -1), midiLine))
	numRests = len(midiLine) - len(filteredLine)

	# stick them back in random places and return the result
	for i in range(numRests):
		filteredLine.insert(random.randint(0, len(filteredLine)), -1)

	return filteredLine
	

# ---------------------Tests---------------------

# Main shows example usage of each function
def main():
	# Test setup/helper functions
	print(TEMPO)
	print(calculateNoteDuration("half"))
	setTempo(180)
	print(TEMPO)
	print(calculateNoteDuration("quarterZ"))
	noteA = fToM(440)
	print(noteA, mToF(noteA))

	# Make some notes
	playNote(60)
	playNote(62, 100, 500, 57)
	playNote(64, duration=1500)

	# Play some melodies
	cScale = [60, 62, 64, 65, 67, 69, 71, 72, -1, 72, 71, 69, 67, 65, 64, 62, 60]
	randomVelocities = []
	for i in range(len(cScale)):
		randomVelocities.append(randomMIDIVal())
	
	playLine(cScale, "eighth")
	playLine(cScale, "sixteenth", randomVelocities, 18)

	# Test the map functions
	playLine(transpose(cScale, 2), "sixteenth", 72, 16)
	playLine(shuffleLine(cScale), "sixteenth", 72, 16)
	playLine(shuffleRests(cScale), "sixteenth", 72, 16)
	playLine(shufflePitches(cScale), "sixteenth", 72, 16)

if __name__ == '__main__':
	main()