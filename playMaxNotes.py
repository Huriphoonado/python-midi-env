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
from musicalSymbols import *
import math

# ---------------------Helper Functions---------------------

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=7123, help="The port the OSC server is listening on")
args = parser.parse_args()
client = udp_client.UDPClient(args.ip, args.port)

TEMPO = 120 # Global tempo variable, determines playback of a line
defaultDur = quarter # Default duration is quarter note if none provided

def setTempo(tempo):
	global TEMPO
	TEMPO = tempo
	return TEMPO

def getTempo():
	global TEMPO
	return TEMPO

# ---------------------Helper Functions---------------------

# Takes a tempo and the note's duration and calculates exact milliseconds
# Current calculations are assuming 4/4 I think...
def calculateNoteDuration(noteLength):
	global TEMPO
	millisecondsPerMeasure = (4/TEMPO) * 60 * 1000

	if type(noteLength) != int and type(noteLength) != float:
		print("Invalid note length included: Using quarter notes")
		return millisecondsPerMeasure/4
	else:
		return millisecondsPerMeasure/noteLength

# generates a random float between 0 and 127
def randomMIDIVal():
	return random.random() * 127.

# Convert a frequency to a midi value
def fToM(frequency):
	return 12 * math.log2(frequency/440) + 69

# Convert a midi value to a frequency
def mToF(midiVal):
	return 440 * math.pow(2, (midiVal - 69)/12)

def getPitch(object):
	if type(object) == int or type(object) == float:
		return object
	elif type(object) == tuple:
		return object[0]

# Set pitch function
# Do not alter a rest unless specified by the function call
def returnNoteWithNewPitch(object, midiToSet, changeRest=False):
	if type(object) == int or type(object) == float:
		if object == -1 and changeRest==False:
			return -1
		else:
			return midiToSet
	elif type(object) == tuple:
		if object[0] == -1 and changeRest==False:
			return (-1, object[1])
		else:
			return (midiToSet, object[1])

# Read rhythm function
def getRhythm(object):
	if type(object) == int or type(object) == float:
		return None
	elif type(object) == tuple:
		return object[1]

# Set rhythm function
def returnNoteWithNewRhythm(object, rhythmToSet):
	if type(object) == int or type(object) == float:
		return (object, rhythmToSet)
	elif type(object) == tuple:
		return (object[0], rhythmToSet)

# Call function to split up noteLine into pitches and rhythms
# If a rhythmic value exists use that, otherwise, default quarterNote
def splitNoteLine(noteLine):
	midiLine = []
	rhythmLine = []

	for note in noteLine:
		if type(note) == int or type(note) == float:
			midiLine.append(note)
			rhythmLine.append(defaultDur)
		elif type(note) == tuple:
			midiLine.append(note[0])
			rhythmLine.append(note[1])
		else:
			print("Oops, something is wrong with the note you provided: " + note)
			return False

	return midiLine, rhythmLine

# ---------------------Make Sounds---------------------

# Sends an OSC Message to Max to play a note via noteout
# MIDI note value required, other parameters optional
# Currently, notes last full duration
# 	Could consider adding a staccato/legato parameter
def playNote(midiVal, velocity=60, noteLength=4, instrument=0):
	duration = calculateNoteDuration(noteLength)
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
# 	Implement: Velocity can be a crescendo or decrescendo calculated by list length
def playLine(noteLine, velocity=60, instrument=0):
	if type(noteLine) != list:
		print("The playLine function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	if splitNoteLine(noteLine) == False:
		return False
	else:
		midiLine, rhythmLine = splitNoteLine(noteLine)

	if type(velocity) == int or type(velocity) == float:
		# Implement - midiVal may be a tuple, use the rhythm value if provided
		[playNote(midiVal, velocity, rhythmVal, instrument) for midiVal, rhythmVal in zip(midiLine, rhythmLine)]
	elif type(velocity) == list:
		# Implement the ability for a shorter velocity list to function (low priority)
		if len(midiLine) == len(velocity):
			[playNote(midiVal, velocityVal, duration, instrument) for midiVal, rhythmVal, velocityVal in zip(midiLine, rhythmLine, velocity)]
		else:
			print("Velocity list is not the same length as the MIDI note list: Playing with volume of mf")
			[playNote(midiVal, mf, rhythmVal, instrument) for midiVal, rhythmVal in zip(midiLine, rhythmLine)]


# ---------------------Map Functions---------------------

# Augment Rhythm
def augment(noteLine):
	if type(noteLine) != list:
		print("The augment function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	augmentedLine = []
	for note in noteLine:
		originalDur = getRhythm(note)
		if originalDur == None:
			augmentedLine.append(returnNoteWithNewRhythm(note, defaultDur/2))
		else:
			augmentedLine.append(returnNoteWithNewRhythm(note, originalDur/2))

	return augmentedLine

# Diminute Rhythm Function
def diminute(noteLine):
	if type(noteLine) != list:
		print("The diminut function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	diminishedLine = []
	for note in noteLine:
		originalDur = getRhythm(note)
		if originalDur == None:
			diminishedLine.append(returnNoteWithNewRhythm(note, defaultDur*2))
		else:
			diminishedLine.append(returnNoteWithNewRhythm(note, originalDur*2))

	return diminishedLine

# Apply Dynamics Function (value, list, crescendo or decresendo)

# Will transpose a list of midinotes, the number of steps provided
def transpose(noteLine, numSteps):
	if type(noteLine) != list:
		print("The transpose function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return

	return list(map((lambda note: returnNoteWithNewPitch(note, getPitch(note) + numSteps)), noteLine))

# changes placement of all pitches and rests
def shuffleLine(noteLine):
	if type(noteLine) != list:
		print("The shuffleLine function must take in a list of MIDI notes. For example: [60, 62, 63]")
		return
	copy = list(noteLine)
	random.shuffle(copy)
	return copy

# Changes pitches, maintains rhythm
# Does not work with tuples update
def shufflePitches(noteLine):
	if type(noteLine) != list:
		print("The shufflePitches function must take in a list of notes. For example: [60, 62, 63]")
		return

	if splitNoteLine(noteLine) == False:
		return False
	else:
		midiLine, rhythmLine = splitNoteLine(noteLine)

	# remove all the rests and shuffle the order of the pitches
	filteredLine = shuffleLine(list(filter((lambda nonRest: nonRest != -1), midiLine)))
	newLine = []

	for note in midiLine:
		if note != -1:
			newLine.append(filteredLine.pop())
		else:
			newLine.append(-1)

	return list(zip(newLine, rhythmLine))

# Changes rhythm, maintains pitches
def shuffleRhythms(noteLine):
	if type(noteLine) != list:
		print("The shuffleRests function must take in a list of notes. For example: [60, 62, 63]")
		return

	if splitNoteLine(noteLine) == False:
		return False
	else:
		midiLine, rhythmLine = splitNoteLine(noteLine)

	# remove all the rests
	filteredLine = list(filter((lambda nonRest: nonRest != -1), midiLine))
	numRests = len(midiLine) - len(filteredLine)

	# stick them back in random places and return the result
	for i in range(numRests):
		filteredLine.insert(random.randint(0, len(filteredLine)), -1)

	shuffledRhythms = list(rhythmLine)
	random.shuffle(shuffledRhythms)

	return list(zip(filteredLine, shuffledRhythms))

# ---------------------Tests---------------------

# Main shows example usage of each function
def main():
	# Test setup/helper functions
	print(TEMPO)
	print(getTempo())
	print(TEMPO)
	print(half)
	print(calculateNoteDuration(half))
	setTempo(180)
	print(TEMPO)
	print(calculateNoteDuration("a"))
	noteA = fToM(440)
	print(noteA, mToF(noteA))

	# Make some notes
	#playNote(60)
	#playNote(62, 100, 500, 57)
	#playNote(64, duration=1500)

	# Play some melodies
	cScale = [60, 62, 64, 65, 67, 69, 71, 72, -1, 72, 71, 69, 67, 65, 64, 62, 60]
	randomVelocities = []
	for i in range(len(cScale)):
		randomVelocities.append(randomMIDIVal())

	playLine(cScale)
	playLine(cScale, randomVelocities, 18)

	# Test the map functions
	playLine(transpose(cScale, 2), 100, 16)
	playLine(shuffleLine(cScale), 100, 16)
	#playLine(shuffleRests(cScale) 100, 16)
	#playLine(shufflePitches(cScale) 100, 16)

if __name__ == '__main__':
	main()
