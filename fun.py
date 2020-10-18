#!/usr/local/bin/python3.8

from Delta import Delta
import music21
from music21 import *
from Movement import Movement
from MyNote import MyNote
import os
from pathlib import Path
from Piece import Piece
import re
import sys

MARK_IN = articulations.StrongAccent()
MARK_OUT = articulations.Accent()

music21.environment.set("musescoreDirectPNGPath", "/Applications/MuseScore 3.app")
music21.environment.set("musicxmlPath", "/Applications/MuseScore 3.app")
music21.environment.set(
    "lilypondPath", "/Applications/LilyPond.app/Contents/Resources/bin/lilypond"
)

FIGURED_BASS_MEASURE_NOTE = {
    1: "G", 2: "F#", 3: "E", 4: "D", 5: "B", 6: "C", 7: "D", 8: "G", 9: "G", 10: "F#", 11: "E", 12: "A", 13: "F#", 14: "G", 15: "A", 16: "D",
    17: "D", 18: "B", 19: "C", 20: "B", 21: "G", 22: "A", 23: "D", 24: "C", 25: "C", 26: "B", 27: "A", 28: "D", 29: "G", 30: "C", 31: "D", 32: "G",
}
MINIMUM_SNIPPET_LENGTH = 7
MOVEMENTS = [
    Movement('Aria', 32, False, {1: 1, 2: 4, 3: 4, 4: 2, 5: 3, 6: 3}),
    Movement('Variation 1', 32, False, {1: 1, 2: 2, 3: 2, 4: 2, 5: 2}),
    Movement('Variation 2', 32, True, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3}),
    Movement('Variation 3', 16, False, {1: 1, 2: 2, 3: 3, 4: 3}),
    Movement('Variation 4', 32, True, {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 3, 7: 4}),
    Movement('Variation 5', 32, False, {1: 1, 2: 2, 3: 2}),
    Movement('Variation 6', 32, True, {1: 2, 2: 1, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3}),
    Movement('Variation 7', 32, False, {1: 1, 2: 2}),
    Movement('Variation 8', 32, False, {1: 1, 2: 2}),
    Movement('Variation 9', 16, False, {1: 1, 2: 2, 3: 3, 4: 3}),
    Movement('Variation 10', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 4}),
    Movement('Variation 11', 32, False, {1: 1, 2: 2, 3: 2, 4: 2}),
    Movement('Variation 12', 32, False, {1: 1, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3}),  # darn part 5 mixes voices 2 and 3 :(
    Movement('Variation 13', 32, False, {1: 1, 2: 3, 3: 3, 4: 2, 5: 4, 6: 4}),
    Movement('Variation 14', 32, False, {1: 1, 2: 2}),
    Movement('Variation 15', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}),
]
PART_COLORS = ["blue", "green", "orange", "purple", "gray", "yellow", "white"]
VOICE_COLOR = {
    1: PART_COLORS[0],
    2: PART_COLORS[1],
    3: PART_COLORS[2],
    4: PART_COLORS[3],
}


def getVoice(movement, part):
    if part in movement.partVoiceMap:
        return movement.partVoiceMap[part]

    return None


def getVoiceColor(movement, voice):
    voiceMap = {
        2: {2: 4},
        3: {3: 4}
    }

    if movement.voices in voiceMap and voice in voiceMap[movement.voices]:
        voice = voiceMap[movement.voices][voice]

    if voice:
        if voice in VOICE_COLOR:
            return VOICE_COLOR[voice]

    if len(PART_COLORS) >= (voice - 1):
        return PART_COLORS[voice - 1]
    else:
        return "gray"


def openMidi(path):
    stream = converter.parse(path)
    stream.insert(0, metadata.Metadata())
    stream.metadata.composer = "Johann Sebastian Bach"
    stream.metadata.movementName = pathToMovement(path).name

    return stream


def snippetToString(snippet):
    return ",".join(map(lambda delta: str(delta.delta), snippet))


def indexDeltas(index, piece):
    for voice in piece.deltas.keys():
        theseDeltas = piece.deltas[voice]

        for i in range(0, len(theseDeltas) - MINIMUM_SNIPPET_LENGTH):
            snippet = theseDeltas[i: i + MINIMUM_SNIPPET_LENGTH]
            snippetString = snippetToString(snippet)
            if not snippetString in index:
                index[snippetString] = []

            index[snippetString].append(
                {
                    "movement": piece.movement,
                    "startingIndex": i,
                    "snippet": snippet,
                    "voice": voice,
                }
            )


def beatInt(beat):
    pair = str(beat).split('/')
    if len(pair) == 1:
        return int(float(pair[0]))
    else:
        return int(float(pair[0]) / float(pair[1]))


def matchIncluded(matched, matchCandidateOne, matchCandidateTwo):
    for matchCandidate in [matchCandidateOne, matchCandidateTwo]:
        for match in matched:
            if matchCandidate['voice'] != match['voice']:
                continue

            if match['i'] <= matchCandidate['i'] and match['j'] >= matchCandidate['j']:
                return True

    return False


def handleDeltas(piece, index):
    matches = {}

    return

    for voice in sorted(piece.deltas.keys()):
        # if voice != 1:
        #     continue

        deltas = piece.deltas[voice]
        mainStream = piece.voiceNoteStreams[voice]

        mainIndex = -1

        matched = []

        while mainIndex < len(deltas) - MINIMUM_SNIPPET_LENGTH:
            mainIndex = mainIndex + 1
            snippet = deltas[mainIndex: mainIndex + MINIMUM_SNIPPET_LENGTH]
            snippetString = snippetToString(snippet)

            if snippetString in index:
                for match in index[snippetString]:
                    if (
                            match["movement"] == piece.movement
                            and match["voice"] == voice
                            and match["startingIndex"] == mainIndex
                    ):
                        continue

                    if match["movement"] != piece.movement:
                        continue

                    if match["startingIndex"] > mainIndex:
                        continue

                    lookAhead = 0
                    mainStart = mainIndex + MINIMUM_SNIPPET_LENGTH
                    childStart = match["startingIndex"] + MINIMUM_SNIPPET_LENGTH

                    if match["voice"] in piece.voiceNoteStreams:
                        childStream = piece.voiceNoteStreams[match["voice"]]
                    else:
                        childStream

                    if (mainStart + lookAhead) > len(mainStream) - 2 or (
                            childStart + lookAhead
                    ) > len(childStream) - 2:
                        continue

                    mainLastOrdinal = MyNote.getNoteOrdinal(mainStream[mainStart - 1])
                    childLastOrdinal = MyNote.getNoteOrdinal(
                        childStream[childStart - 1]
                    )

                    while (mainStart + lookAhead) < len(mainStream) and (
                            childStart + lookAhead
                    ) < len(childStream):
                        mainThisOrdinal = MyNote.getNoteOrdinal(
                            mainStream[mainStart + lookAhead]
                        )
                        childThisOrdinal = MyNote.getNoteOrdinal(
                            childStream[childStart + lookAhead]
                        )

                        mainDelta = mainThisOrdinal - mainLastOrdinal
                        childDelta = childThisOrdinal - childLastOrdinal

                        if mainDelta == childDelta:
                            match
                        else:
                            matchCandidateOne = {
                                'voice': match['voice'],
                                'i': match['startingIndex'],
                                'j': match['startingIndex'] + MINIMUM_SNIPPET_LENGTH + lookAhead
                            }
                            matchCandidateTwo = {
                                'voice': voice,
                                'i': mainIndex,
                                'j': mainIndex + MINIMUM_SNIPPET_LENGTH + lookAhead
                            }

                            if matchIncluded(matched, matchCandidateOne, matchCandidateTwo):
                                break
                            matched.append(matchCandidateOne)
                            matched.append(matchCandidateTwo)

                            firstPart = f"{MINIMUM_SNIPPET_LENGTH + lookAhead + 1} v{match['voice']} {childStream[match['startingIndex']].measureNumber}.{beatInt(childStream[match['startingIndex']].beat)}-{childStream[match['startingIndex'] + lookAhead].measureNumber}.{beatInt(childStream[match['startingIndex'] + lookAhead].beat)}"
                            secondPart = f"v{voice} {mainStream[mainIndex].measureNumber}.{beatInt(mainStream[mainIndex].beat)}-{mainStream[mainIndex + lookAhead].measureNumber}.{beatInt(mainStream[mainIndex + lookAhead].beat)}"

                            if firstPart in matches:
                                matchLetter = matches[firstPart]
                            elif secondPart in matches:
                                matchLetter = matches[secondPart]
                            else:
                                matchLetter = chr(ord('@') + int(len(matches) / 2) + 1)
                                matches[firstPart] = matchLetter
                                matches[secondPart] = matchLetter

                            lyric = f"[{matchLetter}: " + \
                                    f"{firstPart}, " + \
                                    f"{secondPart}"
                            match["snippet"][0].note.addLyric(lyric)
                            match["snippet"][0].note.articulations.append(MARK_IN)
                            match["snippet"][0].note.editorial = editorial.Editorial()
                            match["snippet"][
                                0
                            ].note.editorial.backgroundHighlight = "blue"
                            print(lyric)
                            mainStream[mainStart + lookAhead].addLyric(f"v{voice} {matchLetter}]")
                            mainStream[mainStart + lookAhead].articulations.append(MARK_OUT)
                            childStream[childStart + lookAhead].addLyric(f"v{match['voice']} {matchLetter}]")
                            childStream[childStart + lookAhead].articulations.append(MARK_OUT)
                            mainIndex = mainStart + lookAhead
                            break

                        lookAhead = lookAhead + 1


def noteType(note):
    if note.isChord:
        return "chord"
    elif note.isRest:
        return "rest"
    elif note.isNote:
        return "note"
    else:
        return "hmmm"


def getMeasureBeat(numerator, denominator, offset):
    measureZeroBased = int(offset / (numerator / (denominator / 4)))
    beat = offset - (measureZeroBased * (numerator / (denominator / 4)))
    return measureZeroBased + 1, beat + 1


def getFiguredBassMeasure(movement, beatsPerMeasure, measureNumber, beat):
    # need to handle
    # 2 - has volta repeats
    # 3 - only 16 measures total
    # 9 - only 16 measures total
    # 16 - harder because of time signature changes :(
    # 21 - no repeat?
    # 22 - weird

    if movement.voltaRepeats:
        if measureNumber >= 1 and measureNumber <= 16:
            return measureNumber
        if measureNumber >= 17 and measureNumber <= 33:
            return measureNumber - 1
        else:
            return 32

    if movement.measures == 16:
        adjustedMeasure = measureNumber + (measureNumber - 1)

        if beat >= (beatsPerMeasure / 2) + 1:
            adjustedMeasure = adjustedMeasure + 1

        return adjustedMeasure

    return measureNumber
    # if measureNumber >= 1 and measureNumber <= 16:
    #     return measureNumber
    # elif measureNumber >= 17 and measureNumber <= 32:
    #     return measureNumber - 16
    # elif measureNumber >= 33 and measureNumber <= 48:
    #     return measureNumber - 16
    # elif measureNumber >= 39 and measureNumber <= 64:
    #     return measureNumber - 32
    # elif measureNumber == 65:
    #     return 1
    # else:
    #     return 1


def getFiguredBassNote(movement, numerator, denominator, offset):
    measure, beat = getMeasureBeat(numerator, denominator, offset)
    beatsPerMeasure = numerator / (denominator / 4)
    figuredBassMeasure = getFiguredBassMeasure(movement, beatsPerMeasure, measure, beat)
    return FIGURED_BASS_MEASURE_NOTE[figuredBassMeasure]


def getOutPath(path, type):
    path = path.replace("/musicxml-clean/", f"/xml-out/")
    path = path.replace(".musicxml$", f".{type}")

    pathObject = Path(path)

    if not pathObject.parent.exists():
        pathObject.parent.mkdir()

    return path


def hasNote(stream):
    for candidate in stream.recurse():
        if "isNote" in dir(candidate) and candidate.isNote:
            return True

    return False


def pathToMovement(path):
    movementFilename = re.sub(".+[0-9]{2}\-|\.\w+$", "", path)
    movementFilename = movementFilename.replace("_", " ")

    for thisMovement in MOVEMENTS:
        if thisMovement.name == movementFilename:
            return thisMovement

    print(f"no luck on {path}")
    sys.exit(1)


def ingestFile(path):
    stream = openMidi(path)

    movement = pathToMovement(path)

    # setting time signatures to all parts to the time signature of the 0th
    for i in range(1, len(stream.parts)):
        if not stream.parts[i].timeSignature:
            stream.parts[i].timeSignature = stream.parts[0].timeSignature

    piece = Piece(path, movement, stream)

    partNumber = 0

    voiceOffsetMap = {}

    for part in stream.voicesToParts():
        if not hasNote(part):
            continue

        partNumber = partNumber + 1
        voiceIndex = getVoice(movement, partNumber)
        voiceColor = getVoiceColor(movement, voiceIndex)

        for note in part.recurse():
            if "isRest" not in dir(note) and "isNote" not in dir(note):
                continue

            note.style.color = voiceColor

            totalOffset = note.getOffsetInHierarchy(stream)

            if voiceIndex not in voiceOffsetMap:
                voiceOffsetMap[voiceIndex] = {}

            # if something is already there
            if totalOffset in voiceOffsetMap[voiceIndex]:
                # and the something is a note
                if "isNote" in dir(voiceOffsetMap[voiceIndex][totalOffset]):
                    # and this is a rest, then skip this
                    if "isRest" in dir(note):
                        continue
                    print("hmm")

            voiceOffsetMap[voiceIndex][totalOffset] = note

        part.insert(0, metadata.Metadata())
        part.metadata.movementName = f"part number {partNumber}"
        part.show()

    for voiceIndex in voiceOffsetMap.keys():
        lastNote = None

        voiceStream = piece.getVoiceStream(voiceIndex)
        voiceNoteStream = piece.getVoiceNoteStream(voiceIndex)

        for totalOffset, note in sorted(voiceOffsetMap[voiceIndex].items()):
            if "isRest" in dir(note) and note.isRest:
                voiceStream.append(note)

            if "isNote" in dir(note) and note.isNote:
                pieceVoice = piece.getVoice(voiceIndex)
                pieceDeltas = piece.getDeltas(voiceIndex)

                if note.tie and note.tie.type != 'start':
                    continue

                measure, beat = getMeasureBeat(
                    stream.flat.timeSignature.numerator,
                    stream.flat.timeSignature.denominator,
                    totalOffset
                )

                handleFiguredBass(piece, stream.flat.timeSignature.numerator, stream.flat.timeSignature.denominator, totalOffset, note, measure, beat)

                myNote = MyNote(note)
                pieceVoice.append(myNote)
                if lastNote:
                    pieceDeltas.append(
                        Delta(
                            myNote.noteOrdinal - pieceVoice[len(pieceVoice) - 2].noteOrdinal, lastNote, len(voiceStream), measure, beat
                        )
                    )

                print(
                    f"{voiceIndex} -> {measure} -> {beat} -> {totalOffset} -> {note.nameWithOctave} -> {myNote.noteOrdinal} -> {note.style.color}"
                )
                voiceStream.append(note)
                voiceNoteStream.append(note)

                lastNote = note

    return piece


def handleFiguredBass(piece, numerator, denominator, totalOffset, note, measure, beat):
    figuredBassNote = getFiguredBassNote(
        piece.movement, numerator, denominator, totalOffset
    )
    if note.name == figuredBassNote:
        note.style.color = "gold"
        print(
            f"{measure} -> {beat} -> {figuredBassNote} -> {note.pitch.diatonicNoteNum}"
        )


def getPaths(directory):
    paths = []

    for candidate in os.listdir(directory):
        if candidate.endswith(".musicxml"):
            paths.append(candidate)

    paths.sort()

    return paths


def printDeltas(piece):
    print("notes")
    for voice in piece.voiceNoteStreams:
        noteWithOctaveString = f"   {voice} -> "
        noteOrdinalString = f"   {voice} -> "
        for note in piece.voiceNoteStreams[voice]:
            noteWithOctaveString = noteWithOctaveString + f"{note.nameWithOctave}{note.style.color}, "
            noteOrdinalString = noteOrdinalString + f"{MyNote.getNoteOrdinal(note)}, "

        print(noteWithOctaveString)
        print(noteOrdinalString)

    print("deltas")
    for voice in piece.deltas:
        deltaString = f"   {voice} -> "
        for delta in piece.deltas[voice]:
            deltaString = deltaString + f"{delta.delta}, "

        print(deltaString)


def walkDirectory(directory):
    corpus = {}
    index = {}

    for file in getPaths(directory):
        path = directory + "/" + file

        movement = pathToMovement(path)
        if not movement.name == 'Variation 15':
            continue

        print(f"{path} -> {movement.name}")
        piece = ingestFile(path)
        indexDeltas(index, piece)
        printDeltas(piece)
        corpus[movement] = piece

    for movement in corpus:
        piece = corpus[movement]
        handleDeltas(piece, index)
        writePath(piece.path, piece.stream)


def writePath(path, stream):
    xmlPath = getOutPath(path, 'xml')
    fp = stream.write("musicxml", fp=xmlPath)
    print(f"{xmlPath} was written")


walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean")
