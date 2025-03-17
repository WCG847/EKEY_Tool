import math
import struct
import os
import json

def ReadZYX8(file):
	return [struct.unpack("<b", file.read(1))[0] for i in range(3)]

def ReadINT10(file):
    value = struct.unpack("<H", file.read(2))[0]  # Read 2 bytes as an unsigned short
    value &= 0x03FF  # Extract only the lower 10 bits
    
    # Check if the 10th bit (sign bit) is set
    if value & 0x0200:
        value -= 0x0400  # Apply two's complement sign extension
    
    return value

def ReadINT12(file):
	value = struct.unpack("<H", file.read(2))[0]  # Read 2 bytes as an unsigned short
	value &= 0x0FFF  # Extract only the lower 12 bits
	
	# Check if the 12th bit (sign bit) is set
	if value & 0x0800:
		value -= 0x1000  # Apply two's complement sign extension
	
	return value

def RaiseINT10Errors(value):
	if value < -512 or value > 511:
		raise ValueError("INT10 value out of range: %d" % value)

def RaiseINT12Errors(value):
	if value < -2048 or value > 2047:
		raise ValueError("INT12 value out of range: %d" % value)


def ExpandINT8(value):
	return value / 127.0

def ExpandZYX8(value):
	return [ExpandINT8(value[0]), ExpandINT8(value[1]), ExpandINT8(value[2])]

class CEKey:
	def __init__(self, PAC):
		self.AA = open(PAC, "rb")

	def GetHeaderInfo(self):
		self.EntryCount = struct.unpack("<I", self.AA.read(4))[0]
		if self.EntryCount > 65536:
			raise ValueError("Entry count is too high")
		self.Entries = []
		for i in range(self.EntryCount):
			ChildID = struct.unpack("<H", self.AA.read(2))[0]
			AdultID = struct.unpack("<H", self.AA.read(2))[0]
			RelativeVirtualAddress = struct.unpack("<H", self.AA.read(2))[0] # The following will be highly awkward
			tmp = struct.unpack("<B", self.AA.read(1))[0]
			RVA = ((tmp & 15) << 8) | RelativeVirtualAddress
			self.AA.seek(-1, 1)
			FCount = struct.unpack("<I", self.AA.read(4))[0]
			FrameCount = FCount >> 4
			if FrameCount > 1024:
				raise ValueError("Frame count is too high")
			self.Entries.append({
				"ChildID": ChildID, "AdultID": AdultID, "RVA": RVA, "FrameCount": FrameCount})

	def GetKeyframes(self):
		self.Keyframes = []
		self.Channels = []
		for i in range(self.EntryCount):
			self.AA.seek(self.Entries[i]["RVA"], 0)
			FrameCount = self.Entries[i]["FrameCount"]
			for YukesBullShit in range(FrameCount):
				F_Length = struct.unpack("<B", self.AA.read(1))[0]
				FrameLength = F_Length & 127
				Channel_Count = struct.unpack("<B", self.AA.read(1))[0]
				Joint_Count = (Channel_Count - 3 // 3)
				for highly_unorthodox in range(Joint_Count):
					'''ROOT = 6 CHANNELS'''
					RootPos = ExpandZYX8(ReadZYX8(self.AA))
					RootRot = ExpandZYX8(ReadZYX8(self.AA))
					'''JOINTS = 3 CHANNELS'''







				




