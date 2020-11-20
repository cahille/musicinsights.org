class Movement:
    def __init__(self, name, measures, voltaRepeats, partVoiceMap, beatsPath=None, partOffsetMap={}):
        self.name = name
        self.measures = measures
        self.voltaRepeats = voltaRepeats
        self.partVoiceMap = partVoiceMap
        self.partOffsetMap = partOffsetMap

        if beatsPath != None:
            self.beatDurations = []

            beatsFile = open(beatsPath, 'r')
            lastTime = None

            while True:
                line = beatsFile.readline()

                if line:
                    thisTime = float(line.strip())

                    if lastTime:
                        self.beatDurations.append(thisTime - lastTime)

                    lastTime = thisTime
                else:
                    break

        self.voices = None

        for voice in partVoiceMap.values():
            if self.voices == None or voice > self.voices:
                self.voices = voice
