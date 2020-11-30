import music21


class Piece:
    deltas = None
    path = None
    movement = None
    stream = None
    voiceNoteArrays = None
    voices = None
    voiceArrays = None

    def __init__(self, path, movement, stream):
        self.path = path
        self.movement = movement
        self.stream = stream
        self.deltas = {}
        self.voices = {}
        self.voiceArrays = {}
        self.voiceNoteArrays = {}
        self.figuredBassReports = {
            'counts': {}
        }

    def getVoice(self, voiceIndex):
        if voiceIndex not in self.voices:
            self.voices[voiceIndex] = []

        return self.voices[voiceIndex]

    def getDeltas(self, voiceIndex):
        if voiceIndex not in self.deltas:
            self.deltas[voiceIndex] = []

        return self.deltas[voiceIndex]

    def getVoiceArray(self, voiceIndex):
        if not voiceIndex in self.voiceArrays:
            self.voiceArrays[voiceIndex] = []

        return self.voiceArrays[voiceIndex]

    def getVoiceNoteArray(self, voiceIndex):
        if not voiceIndex in self.voiceNoteArrays:
            self.voiceNoteArrays[voiceIndex] = []

        return self.voiceNoteArrays[voiceIndex]

    def getNumerator(self):
        return self.stream.flat.timeSignature.numerator

    def getDenominator(self):
        return self.stream.flat.timeSignature.denominator

    def backInBlack(self):
        for element in self.stream.flat:
            if "isNote" in dir(element):
                element.style.color = 'black'
