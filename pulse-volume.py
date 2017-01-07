#!/usr/bin/env python

import optparse
import re
import subprocess
import sys

class Volume:
	def __init__(self, options):
		self.options = options
		self.state = None
		self.modified = False

	def get_state(self):
		"""Return a string output from pacmd list-sinks
		"""
		if self.state is None or self.modified:
			self.state = subprocess.check_output(["pacmd", "list-sinks"])
		return self.state

	def get_default_sink(self):
		"""Return the index of the default sink
		"""
		match = re.search(r"^\s*\*\s*index:\s*(\d+)$", self.get_state(), flags=re.MULTILINE)
		if not match:
			raise Exception("couldn't find default sink in pacmd's output: %s" % self.get_state())
		return int(match.group(1))

	def get_volume(self):
		"""Return the volume (integer 0 to maximum volume, which might be 65000 or 
		whatever)
		"""
		correctSink = False
		for line in self.get_state().split("\n"):
			if not correctSink:
				if re.search(r"^[\s*]*index: %d$" % self.options.sink, line):
					correctSink = True
				continue
			match = re.search(r"^\s*volume:\s+front-left:\s+(\d+)", line)
			if match:
				return int(match.group(1))
		raise Exception("couldn't find volume in pacmd's output: %s" % self.get_state())

	def get_mute(self):
		"""Return true if the sink is muted
		"""
		return bool(re.search(r"^\s*muted: yes$", self.get_state(), flags=re.MULTILINE))

	def get_max_volume(self):
		"""Return the maximum volume (integer, 65000 or whatever)
		"""
		match = re.search(r"^\s*volume steps:\s+(\d+)$", self.get_state(), flags=re.MULTILINE)
		if not match:
			raise Exception("couldn't find volume steps in pacmd's output: %s" % self.get_state())
		return int(match.group(1))

	def set_mute(self, muted=True):
		"""Switch on mute, or switch it off if passed False
		"""
		subprocess.call(["pactl", "set-sink-mute", str(self.options.sink), str(int(muted))])
		self.modified = True

	def set_volume(self, volume):
		"""Set the volume (integer 0 to maximum volume, which might be 65000 or 
		whatever). Silently caps to 0 or maximum volume if given an argument out of 
		range.
		"""
		if volume < 0:
			volume = 0
		else:
			volume = min(volume, self.get_max_volume())
		subprocess.call(["pactl", "set-sink-volume", str(self.options.sink), str(volume)])
		self.modified = True

	def vol_string(self):
		"""Return a string describing the current volume
		"""
		vol = self.get_volume()
		maxvol = self.get_max_volume()
		return "%d/%d (%d%%)" % (vol, maxvol, int(100 * float(vol) / maxvol))

	def mute_string(self):
		"""Return a string describing the current mute state
		"""
		if self.get_mute():
			return "yes"
		return "no"

if __name__ == "__main__":
	optionparser = optparse.OptionParser(usage="%prog [options] [<volume>[%][+|-]]")
	optionparser.add_option("-q", "--quiet", action="store_true", help="Don't print the new volume and mute status")
	optionparser.add_option("-s", "--sink", type="int", default=-1, help="Set the sink number to control (default: %default, which means use Pulse default)")
	optionparser.add_option("--toggle", action="store_true", help="Toggle mute status")
	optionparser.add_option("--unmute", action="store_true", help="Unmute")
	optionparser.add_option("--mute", action="store_true", help="Mute")
	optionparser.add_option("--muted", action="store_true", help="Exit with success status (0) if muted, 1 if not muted, do nothing else")
	(options, args) = optionparser.parse_args()

	if len(args) > 1:
		optionparser.error("Expected either no non-option arguments or one non-option argument")
	if options.unmute and options.mute:
		optionparser.error("--unmute and --mute connot be used at the same time")

	volume = Volume(options)

	if options.sink == -1:
		options.sink = volume.get_default_sink()

	if options.muted:
		sys.exit(0 if volume.get_mute() else 1)

	if options.toggle:
		volume.set_mute(not volume.get_mute())
	elif options.mute:
		volume.set_mute()
	elif options.unmute:
		volume.set_mute(False)

	if len(args) == 1:
		match = re.search(r"^(\d+)(%?)([+-]?)$", args[0])
		if not match:
			optionparser.error("Unrecognized argument")

		amount = int(match.group(1))
		percentage = match.group(2) == r"%"
		relative = len(match.group(3)) > 0
		increment = match.group(3) == "+"

		if percentage:
			amount = int(round(float(volume.get_max_volume()) * amount / 100))
		if relative:
			base = volume.get_volume()
			if increment:
				amount += base
			else:
				amount = base - amount

		volume.set_volume(amount)

	if not options.quiet:
		print "%s (muted: %s)" % (volume.vol_string(), volume.mute_string())
