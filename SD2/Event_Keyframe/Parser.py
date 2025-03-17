import struct


def ReadZYX8(file):
    return [struct.unpack("<b", file.read(1))[0] for i in range(3)]


def ReadZY8(file):
    return [struct.unpack("<b", file.read(1))[0] for i in range(2)]


def ReparseRootPos(file):
    """Attempts to reparse RootPos using INT10 or INT12 if possible, otherwise defaults to ZYX8."""
    # Read the initial ZYX8 values
    root_x, root_y, root_z = ReadZYX8(file)

    # Define mapping of functions and range checks
    int_methods = [(CheckINT10, ReadINT10), (CheckINT12, ReadINT12)]

    for check_func, read_func in int_methods:
        if check_func(root_x) and check_func(root_y) and check_func(root_z):
            return [read_func(file), read_func(file), read_func(file)]

    # If neither INT10 nor INT12 works, fallback to expanded ZYX8
    return ExpandZYX8([root_x, root_y, root_z])


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


def CheckINT10(value):
    if value < -512 or value > 511:
        return False
    return True


def CheckINT12(value):
    if value < -2048 or value > 2047:
        return False
    return True


def ExpandINT8(value):
    return value / 127.0


def ExpandZYX8(value):
    return [ExpandINT8(value[0]), ExpandINT8(value[1]), ExpandINT8(value[2])]


def ExpandZY8(value):
    return [ExpandINT8(value[0]), ExpandINT8(value[1])]


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
            RelativeVirtualAddress = struct.unpack("<H", self.AA.read(2))[
                0
            ]  # The following will be highly awkward
            tmp = struct.unpack("<B", self.AA.read(1))[0]
            RVA = ((tmp & 15) << 8) | RelativeVirtualAddress
            self.AA.seek(-1, 1)
            FCount = struct.unpack("<I", self.AA.read(4))[0]
            FrameCount = FCount >> 4
            if FrameCount > 1024:
                raise ValueError("Frame count is too high")
            self.Entries.append(
                {
                    "ChildID": ChildID,
                    "AdultID": AdultID,
                    "RVA": RVA,
                    "FrameCount": FrameCount,
                }
            )

    def GetKeyframes(self):
        self.Keyframes = []
        self.Channels = []
        for i in range(self.EntryCount):
            self.AA.seek(self.Entries[i]["RVA"], 0)
            FrameCount = self.Entries[i]["FrameCount"]
            for YukesBullShit in range(FrameCount):
                F_Length = struct.unpack("<B", self.AA.read(1))[0]
                FrameLength = F_Length & 127
                for WHYYYYYYYYY in range(FrameLength):
                    CC = struct.unpack("<B", self.AA.read(1))[0]
                    Flag = CC & 15
                    Channel_Count = CC & 240
                    if Channel_Count >= 60:
                        """Read Joint Data as Halfwords"""
                        pass
                    elif Channel_Count <= 30:
                        pass

                    Joint_Count = Channel_Count - 3 // 3
                    for highly_unorthodox in range(Joint_Count):
                        joint_data = {
                            "RootPos": ReparseRootPos(self.AA),
                            "RootRot": ExpandZYX8(ReadZYX8(self.AA)),
                            "SpineLRot": ExpandZYX8(ReadZYX8(self.AA)),
                            "SpineURot": ExpandZYX8(ReadZYX8(self.AA)),
                            "NeckRot": ExpandZY8(ReadZY8(self.AA)),
                            "HeadRot": ExpandZYX8(ReadZYX8(self.AA)),
                            "LeftShoulderRot": ExpandZY8(ReadZY8(self.AA)),
                            "LeftArmRot": ExpandZYX8(ReadZYX8(self.AA)),
                            "LeftForeArmRot": ExpandZY8(ReadZY8(self.AA)),
                            "LeftHandRot": ExpandZY8(ReadZY8(self.AA)),
                            "RightShoulderRot": ExpandZY8(ReadZY8(self.AA)),
                            "RightArmRot": ExpandZYX8(ReadZYX8(self.AA)),
                            "RightForeArmRot": ExpandZY8(ReadZY8(self.AA)),
                            "RightHandRot": ExpandZY8(ReadZY8(self.AA)),
                            "LeftHipRot": ExpandZYX8(ReadZYX8(self.AA)),
                            "LeftLegRot": struct.unpack("<b", self.AA.read(1))[0],  # X
                            "LeftFootRot": ExpandZY8(ReadZY8(self.AA)),
                            "RightHipRot": ExpandZYX8(ReadZYX8(self.AA)),
                            "RightLegRot": struct.unpack("<b", self.AA.read(1))[0],  # X
                            "RightFootRot": ExpandZY8(ReadZY8(self.AA)),
                        }

                        # Store the joint data in a list or another structure as needed
                        self.Keyframes.append(joint_data)


