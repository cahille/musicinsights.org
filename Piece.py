import music21


class Piece:
    deltas = None
    path = None
    movement = None
    stream = None
    voiceNoteStreams = None
    voices = None
    voiceStreams = None

    def __init__(self, path, movement, stream):
        self.path = path
        self.movement = movement
        self.stream = stream
        self.deltas = {}
        self.voices = {}
        self.voiceStreams = {}
        self.voiceNoteStreams = {}
        self.figuredBassReports = {
            'counts' : {}
        }

    def getVoice(self, voiceIndex):
        if voiceIndex not in self.voices:
            self.voices[voiceIndex] = []

        return self.voices[voiceIndex]

    def getDeltas(self, voiceIndex):
        if voiceIndex not in self.deltas:
            self.deltas[voiceIndex] = []

        return self.deltas[voiceIndex]

    def getVoiceStream(self, voiceIndex):
        if not voiceIndex in self.voiceStreams:
            self.voiceStreams[voiceIndex] = music21.stream.Stream()

        return self.voiceStreams[voiceIndex]

    def getVoiceNoteStream(self, voiceIndex):
        if not voiceIndex in self.voiceNoteStreams:
            self.voiceNoteStreams[voiceIndex] = music21.stream.Stream()

        return self.voiceNoteStreams[voiceIndex]

    def getNumerator(self):
        return self.stream.flat.timeSignature.numerator

    def getDenominator(self):
        return self.stream.flat.timeSignature.denominator
