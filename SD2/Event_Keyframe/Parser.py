import math
import struct
import os
import json


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
			return self.Entries

	def GetKeyframes(self):
		self.Keyframes = []
		for i in range(self.EntryCount):
			self.AA.seek(self.Entries[i]["RVA"], 0)
			FrameCount = self.Entries[i]["FrameCount"]
			Keyframes = []
			for YukesBullShit in range(FrameCount):
				F_Length = struct.unpack("<B", self.AA.read(1))[0]
				FrameLength = F_Length & 127
				Channel_Count = struct.unpack("<B", self.AA.read(1))[0]
				Joint_Count = ((FrameLength - 2) // 3) + 1

				




