class Movement:
    def __init__(self, name, measures, voltaRepeats, partVoiceMap):
        self.name = name
        self.measures = measures
        self.voltaRepeats = voltaRepeats
        self.partVoiceMap = partVoiceMap

        self.voices = None

        for voice in partVoiceMap.values():
            if self.voices == None or voice > self.voices:
                self.voices = voice