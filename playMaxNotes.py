# Play Note Function
# Eventually a Play melody function that takes in a list of notes
# 	 Time delays between each note that is determined by a tempo variable
#	 Metronome will affect a delay between notes played
# Map functions that mess with that list
# 	 Would be cool to map a dynamics list as well

import argparse
from pythonosc import osc_message_builder
from pythonosc import udp_client
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=7123, help="The port the OSC server is listening on")
args = parser.parse_args()
client = udp_client.UDPClient(args.ip, args.port)

def playNote(midiVal):
	msg = osc_message_builder.OscMessageBuilder(address = "/playNote")
	msg.add_arg(midiVal)
	msg = msg.build()
	client.send(msg)

def main():
	playNote(60)
	sleep(1)
	playNote(62)
	sleep(1)
	playNote(64)

if __name__ == '__main__':
	main()