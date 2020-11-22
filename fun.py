#!/usr/local/bin/python3.8

from Delta import Delta
import music21
from music21 import *
from Movement import Movement
from music21.exceptions21 import Music21Exception
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
MINIMUM_SNIPPET_LENGTH = 5
COLORS = ['blue', 'green', 'orange', 'purple', 'gray', 'yellow', 'white']
MOVEMENTS = [
    Movement('Aria', 32, False, {1: 1, 2: 2, 3: 2, 4: 2, 5: 3, 6: 4, 7: 4}, partOffsetMap={
        4: {2: [[57, 60]],
            3: [[69, 69]],
            4: [[84, 95]]},
        5: {2: [[2, 2], [18.5, 20.75], [27, 27], [46, 47.5], [54.5, 56.5], [78, 79]],
            4: [[21, 24], [30, 35.5], [42, 42], [52, 52], [48, 53], [57, 75], [81, 83.5]]},
        6: {3: [[1, 1], [68.5, 68.5]]}
    }),
    # Movement('Variation 1', 32, False, {1: 1, 2: 2, 3: 2, 4: 2, 5: 2}, '/Users/earlcahill/Desktop/movies/sync fun/02-variation 1.beats'),
    Movement('Variation 1', 32, False, {1: 1, 2: 2, 3: 1, 4: 2, 5: 2}),
    Movement('Variation 2', 32, True, {1: 1, 2: 2, 3: 3, 4: 3}),
    Movement('Variation 3', 16, False, {1: 1, 2: 2, 3: 3, 4: 3}),
    Movement('Variation 4', 32, True, {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 3, 7: 4}),
    Movement('Variation 5', 32, False, {1: 1, 2: 2, 3: 2}),
    Movement('Variation 6', 32, True, {1: 1, 2: 2, 3: 4, 4: 4, 5: 3, 6: 3, 7: 3, 8: 3}, partOffsetMap={
        3: {1: [[33, 34.25]]},
        5: {2: [[9, 11.75], [21, 22.5], [24, 24], [25.5, 25.5]]},
        7: {2: [[12, 12]]}
    }),
    Movement('Variation 7', 32, False, {1: 1, 2: 2}),
    Movement('Variation 8', 32, False, {1: 1, 2: 2}),
    Movement('Variation 9', 16, False, {1: 1, 2: 2, 3: 3, 4: 3}),
    Movement('Variation 10', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4}, partOffsetMap={
        3: {3: [[16, 38], [44, 62], [112, 126]]},
        4: {3: [[24, 27], [32, 34], [40, 42]]}
    }),
    Movement('Variation 11', 32, False, {1: 1, 2: 2, 3: 2, 4: 2}),
    Movement('Variation 12', 32, False, {1: 1, 2: 2, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3}, partOffsetMap={
        5: {3: [[12, 14], [30, 32.5], [39, 47], [60.5, 72], [75, 83.75]]}
    }),
    Movement('Variation 13', 32, False, {1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4}, partOffsetMap={
        4: {2: [[13, 13]]}
    }),
    Movement('Variation 14', 32, False, {1: 1, 2: 2}),
    Movement('Variation 15', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}, partOffsetMap={
        4: {2: [[4, 7.25], [12, 13.875], [24.5, 27.25], [28.5, 29.75], [52, 53.5], [60, 62]]},
        5: {2: [[14, 14], [54, 54.5]]}
    }),
    Movement('Variation 16', 48, True, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4, 6: 4}, partOffsetMap={
        3: {3: [[117.5, 117.5]]},
        4: {3: [[0, 0], [3.75, 4], [53.75, 54]]}
    }),
    Movement('Variation 17', 32, False, {1: 1, 2: 2}),
    Movement('Variation 18', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4}),
    Movement('Variation 19', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}, partOffsetMap={
        4: {2: [[24, 24.5], [42, 47]]},
        5: {2: [[25.5, 25.5]]}
    }),
    Movement('Variation 20', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}),
    Movement('Variation 21', 16, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 3}, partOffsetMap={
        4: {2: [[0, 7.5], [20, 23.5], [60.75, 62]]},
        5: {2: [[43, 45], [48.25, 49.75]]},
    }),
    Movement('Variation 22', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4}, partOffsetMap={
        # 3: {3: [[34, 44], [50, 60], [78, 92], [98, 104], [112, 112]],
        #     4: [[68, 75], [96, 103]]},
        3: {3: [[34, 44], [50, 60], [78, 78], [84, 92], [106, 111], [116, 124]],
            4: [[68, 75], [96, 103]]},  # , [64, 112], [116, 124]]},
        4: {4: [[32, 56], [64, 110], [116, 118], [124, 124]]},  # , [64, 112], [116, 124]]},
        5: {3: [[80, 83]]},
    }),
    Movement('Variation 23', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4}, partOffsetMap={
        3: {3: [[54.25, 57.5]]},
        4: {3: [[73.25, 95], [48.25, 51.5]]},
    }),
    Movement('Variation 24', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4, 6: 4}, partOffsetMap={
        3: {2: [[15, 17.5]]},
        4: {2: [[9, 13], [45, 51], [63, 66], [63, 95.5], [117, 121], [126.5, 143]]},
        5: {2: [[13, 13.5], [54, 56.5], [67.5, 67.5], [122, 124.5]]},
        6: {4: [[54, 58]]}
    }),
    Movement('Variation 25', 32, True, {1: 1, 2: 3, 3: 4, 4: 3, 5: 4}),
    # Movement('Variation 26', 32, False, {1: 1, 2: 2, 3: 4, 4: 3, 5: 3, 6: 4}),
    Movement('Variation 27', 32, False, {1: 1, 2: 2, 3: 4, 4: 3, 5: 3, 6: 4}),
    Movement('Variation 28', 32, False, {1: 1, 2: 2, 3: 4, 4: 3, 5: 4}, partOffsetMap={
        3: {3: [[18.125, 23.875], [36.125, 44.875], [60.125, 68.875], [36.125, 44.875], [60.125, 68.875], [72.125, 77.875]]},
        4: {4: [[18, 77]]},
    }),
    Movement('Variation 29', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4}, partOffsetMap={
        2: {4: [[24, 56], [84, 90]]},
        3: {1: [[36, 48], [45.75, 46.75], [54, 60], [72, 78]]},
        4: {4: [[39, 45], [54, 60]]}
    }),
    Movement('Variation 30', 16, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 4}),
    Movement('Aria da capo', 32, False, {1: 2, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 4, 8: 1, 9: 1}),
]
VOICE_COLOR = {
    1: COLORS[0],
    2: COLORS[1],
    3: COLORS[2],
    4: COLORS[3],
}


def getVoiceIndex(movement, part, totalOffset):
    if part in movement.partOffsetMap:
        for voiceCandidate in movement.partOffsetMap[part].keys():
            for thisRange in movement.partOffsetMap[part][voiceCandidate]:
                if totalOffset >= thisRange[0] and totalOffset <= thisRange[1]:
                    return voiceCandidate

    if part in movement.partVoiceMap:
        return movement.partVoiceMap[part]

    return None


def getVoiceColor(voice):
    if voice in VOICE_COLOR:
        return VOICE_COLOR[voice]

    if len(COLORS) >= (voice - 1):
        return COLORS[voice - 1]
    else:
        return "gray"


def openMusicFile(path):
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
                    'movement': piece.movement,
                    'startingIndex': i,
                    'snippet': snippet,
                    'voice': voice,
                }
            )

def beatInt(beat):
    pair = str(beat).split('/')
    if len(pair) == 1:
        return int(float(pair[0]))
    else:
        return int(float(pair[0]) / float(pair[1]))


def matchIncluded(matched, matchCandidate):
    for match in matched:
        if matchCandidate['voice'] != match['voice']:
            continue

        if match['i'] <= matchCandidate['startingIndex'] and match['j'] >= matchCandidate['startingIndex']:
            return True

    return False


def handleDeltas(piece, index):
    matches = {}
    matched = []

    for voice in sorted(piece.deltas.keys()):
        mainStream = piece.voiceNoteStreams[voice]

        for snippet in index.keys():
            main = index[snippet][0]

            if matchIncluded(matched, main):
                continue

            for deltaIndex in range(1, len(index[snippet])):
                child = index[snippet][deltaIndex]

                # if child['movement'] != piece.movement:
                #     continue

                if main['voice'] == child['voice']:
                    continue

                if matchIncluded(matched, child):
                    continue

                childStream = piece.voiceNoteStreams[child['voice']]

                mainStartingLoopIndex = main['startingIndex'] + MINIMUM_SNIPPET_LENGTH
                childStartingLoopIndex = child['startingIndex'] + MINIMUM_SNIPPET_LENGTH

                mainLastNote = mainStream[mainStartingLoopIndex - 1]
                childLastNote = childStream[childStartingLoopIndex - 1]

                for lookAhead in range(0, len(mainStream) - mainStartingLoopIndex):
                    print(f"    lookahead - {lookAhead}")

                    thisMainIndex = mainStartingLoopIndex + lookAhead
                    thisChildIndex = childStartingLoopIndex + lookAhead

                    mainNote = mainStream[thisMainIndex]
                    childNote = childStream[thisChildIndex]

                    print(f"mainNote: {mainNote.nameWithOctave}")
                    print(f"childNote: {childNote.nameWithOctave}")

                    if ((thisMainIndex + 1) == len(mainStream)) or ((thisChildIndex + 1) == len(childStream)) \
                            or (
                            (MyNote.getNoteOrdinal(mainNote) - MyNote.getNoteOrdinal(mainLastNote)) != (MyNote.getNoteOrdinal(childNote) - MyNote.getNoteOrdinal(childLastNote))):
                        matchCandidateOne = {'voice': voice, 'i': mainStartingLoopIndex, 'j': thisMainIndex - 1}
                        matchCandidateTwo = {'voice': child['voice'], 'i': child['startingIndex'], 'j': thisChildIndex - 1}

                        matched.append(matchCandidateOne)
                        matched.append(matchCandidateTwo)

                        matchLength = MINIMUM_SNIPPET_LENGTH + lookAhead + 1

                        # the -1 for endnotes is because this note didn't match
                        mainStartNote = mainStream[main['startingIndex']]

                        if ((thisMainIndex + 1) == len(mainStream)) or ((thisChildIndex + 1) == len(childStream)):
                            mainEndNote = mainStream[thisMainIndex]
                            childEndNote = childStream[thisChildIndex]
                        else:
                            mainEndNote = mainStream[thisMainIndex - 1]
                            childEndNote = childStream[thisChildIndex - 1]

                        childStartNote = childStream[child['startingIndex']]

                        mainPart = f"v{voice} {getMeasureBeatString(piece, mainStartNote)}-" + f"{getMeasureBeatString(piece, mainEndNote)}"
                        childPart = f"v{child['voice']} {getMeasureBeatString(piece, childStartNote)}" + f"-{getMeasureBeatString(piece, childEndNote)}"

                        if childPart in matches:
                            matchLetter = matches[childPart]['letter']
                            matchLength = matches[childPart]['length']
                        elif mainPart in matches:
                            matchLetter = matches[mainPart]['letter']
                            matchLength = matches[mainPart]['length']
                        else:
                            matchLetter = chr(ord('@') + int(len(matches) / 2) + 1)
                            thisMatch = {'letter': matchLetter, 'length': matchLength}
                            matches[mainPart] = thisMatch
                            matches[childPart] = thisMatch

                        mainStartNote.articulations.append(MARK_IN)
                        childStartNote.articulations.append(MARK_IN)

                        if mainEndNote.articulations == None or (len(mainEndNote.articulations) == 0) or (
                                len(mainEndNote.articulations) > 0 and mainEndNote.articulations[0] == MARK_IN):
                            mainEndNote.articulations.append(MARK_OUT)

                        if childEndNote.articulations == None or (len(childEndNote.articulations) == 0) or (
                                len(childEndNote.articulations) > 0 and childEndNote.articulations[0] == MARK_IN):
                            childEndNote.articulations.append(MARK_OUT)

                        addLyrics = True
                        if addLyrics:
                            movementReference = ''
                            if child['movement'] != piece.movement:
                                movementReference = f"{child['movement']}: "

                            mainLyric = f"[{matchLetter}: {matchLength} " + \
                                        f"{mainPart}, " + \
                                        f"{movementReference}{childPart}"

                            mainStartNote.addLyric(mainLyric)
                            mainEndString = f"v{voice} {matchLetter}]"
                            if mainEndNote.lyric == None or not mainEndString in mainEndNote.lyric:
                                mainEndNote.addLyric(mainEndString)

                            if child['movement'] == piece.movement:
                                childLyric = f"[{matchLetter}: {matchLength} " + \
                                             f"{childPart}, " + \
                                             f"{mainPart}"

                                childStartNote.addLyric(childLyric)

                                childEndString = f"v{child['voice']} {matchLetter}]"
                                if childEndNote.lyric == None or not childEndString in childEndNote.lyric:
                                    childEndNote.addLyric(childEndString)

                        break
                    else:
                        mainLastNote = mainNote
                        childLastNote = childNote

                        continue


def getMeasureBeat(piece, offset):
    measureZeroBased = int(offset / (piece.getNumerator() / (piece.getDenominator() / 4)))
    beat = offset - (measureZeroBased * (piece.getNumerator() / (piece.getDenominator() / 4)))
    return measureZeroBased + 1, beat + 1


def getOffset(piece, note):
    offset = None
    for candidate in piece.stream.flat:
        if candidate.id == note.id:
            offset = candidate.getOffsetBySite(piece.stream.flat)
            break

    return offset


def getSyncBeat(piece, note):
    offset = getOffset(piece, note)
    measureZeroBased = int(offset / (piece.getNumerator() / (piece.getDenominator() / 4)))
    beat = offset - (measureZeroBased * (piece.getNumerator() / (piece.getDenominator() / 4)))


def getMeasureBeatString(piece, note):
    offset = getOffset(piece, note)
    measure, beat = getMeasureBeat(piece, offset)
    return f"{measure}.{int(beat)}"


def getFiguredBassMeasure(movement, beatsPerMeasure, measureNumber, beat):
    # need to handle
    # 2 - has volta repeats
    # 3 - only 16 measures total
    # 9 - only 16 measures total
    # 16 - harder because of time signature changes :(
    # 21 - no repeat?
    # 22 - weird

    if movement.voltaRepeats:
        if movement.name.endswith('25'):
            measureMap = {
                34: 31,
                35: 32
            }
            if measureNumber in measureMap:
                return measureMap[measureNumber]

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


def getFiguredBassNote(piece, offset):
    measure, beat = getMeasureBeat(piece, offset)
    beatsPerMeasure = piece.getNumerator() / (piece.getDenominator() / 4)
    figuredBassMeasure = getFiguredBassMeasure(piece.movement, beatsPerMeasure, measure, beat)

    if figuredBassMeasure not in FIGURED_BASS_MEASURE_NOTE:
        figuredBassMeasure = 32

    return FIGURED_BASS_MEASURE_NOTE[figuredBassMeasure]


def getOutPath(path, type):
    path = path.replace("/musicxml-clean/", f"/{type}-out/")
    path = path.replace(".musicxml", f".{type}")

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
    thisStream = openMusicFile(path)

    movement = pathToMovement(path)

    # setting time signatures to all parts to the time signature of the 0th
    for i in range(1, len(thisStream.parts)):
        if not thisStream.parts[i].timeSignature:
            thisStream.parts[i].timeSignature = thisStream.parts[0].measure(1).timeSignature

    piece = Piece(path, movement, thisStream)

    return piece


def colorFiguredBass(piece):
    partNumber = 0

    for part in piece.stream.voicesToParts():
        if not hasNote(part):
            continue

        partNumber = partNumber + 1

        for note in part.recurse():
            if "isRest" not in dir(note) and "isNote" not in dir(note):
                continue

            totalOffset = note.getOffsetInHierarchy(piece.stream)
            voiceIndex = getVoiceIndex(piece.movement, partNumber, totalOffset)
            measure, beat = getMeasureBeat(piece, totalOffset)
            handleFiguredBassNote(piece, voiceIndex, totalOffset, note, measure)

    print(f"figured bass report for {piece.movement.name}")

    piece.figuredBassReports['matchingMeasures'] = 0
    piece.figuredBassReports['matchingNotes'] = 0
    piece.figuredBassReports['missingMeasures'] = []

    for measure in range(1, 33):
        if measure in piece.figuredBassReports['counts']:
            for voiceIndex in piece.figuredBassReports['counts'][measure].keys():
                count = piece.figuredBassReports['counts'][measure][voiceIndex]
                piece.figuredBassReports['matchingMeasures'] += 1
                piece.figuredBassReports['matchingNotes'] += count
        else:
            count = 0
            piece.figuredBassReports['missingMeasures'].append(measure)

        print(f" -> {measure} -> {count}")
    print(f" -> {piece.figuredBassReports['matchingMeasures']} matching measures")
    print(f" -> {piece.figuredBassReports['matchingNotes']} matching notes")
    print(f" -> {piece.figuredBassReports['missingMeasures']} missing measures\n")


def handlePartsVoices(piece):
    partNumber = 0

    voiceOffsetMap = {}

    for part in piece.stream.voicesToParts():
        if not hasNote(part):
            continue

        partNumber += 1

        part.insert(0, metadata.Metadata())
        part.metadata.movementName = f"part number {partNumber}"
        part.show()

        for note in part.recurse():
            if "isRest" not in dir(note) and "isNote" not in dir(note) and "isChord" not in dir(note):
                continue

            totalOffset = note.getOffsetInHierarchy(piece.stream)
            voiceIndex = getVoiceIndex(piece.movement, partNumber, totalOffset)

            if "isChord" in (dir(note)) and note.isChord:
                if voiceIndex == 1:
                    note = note.notes[0]
                elif voiceIndex == 4:
                    note = note.notes[-1]
                else:
                    note

            if "isNote" in (dir(note)) and note.isNote:
                print(f"p{partNumber} -> v{voiceIndex} -> {totalOffset} -> {note.nameWithOctave}")

            if voiceIndex not in voiceOffsetMap:
                voiceOffsetMap[voiceIndex] = {}

            if "isRest" in dir(note) and note.isRest:
                continue

            # if something is already there
            if totalOffset in voiceOffsetMap[voiceIndex]:
                # and the something is a note
                if "isNote" in dir(voiceOffsetMap[voiceIndex][totalOffset]):
                    print("hmm")

            voiceOffsetMap[voiceIndex][totalOffset] = note

    for voiceIndex in voiceOffsetMap.keys():
        lastNote = None

        voiceStream = piece.getVoiceStream(voiceIndex)
        voiceNoteStream = piece.getVoiceNoteStream(voiceIndex)

        for totalOffset, note in sorted(voiceOffsetMap[voiceIndex].items()):
            if "isRest" not in dir(note) and "isNote" not in dir(note) and "isChord" not in dir(note):
                continue

            voiceStream.append(note)

            if "isRest" in dir(note) and note.isRest:
                continue

            if "isNote" in dir(note) and note.isNote:
                pieceVoice = piece.getVoice(voiceIndex)
                pieceDeltas = piece.getDeltas(voiceIndex)

                if note.tie and note.tie.type != 'start':
                    continue

                voiceNoteStream.append(note)

                measure, beat = getMeasureBeat(piece, totalOffset)
                myNote = MyNote(note)

                print(
                    f"v{voiceIndex} -> {measure} -> {beat} -> {totalOffset} -> {note.nameWithOctave} -> {myNote.noteOrdinal}"
                )

                pieceVoice.append(myNote)
                if lastNote:
                    pieceDeltas.append(
                        Delta(
                            myNote.noteOrdinal - pieceVoice[len(pieceVoice) - 2].noteOrdinal, lastNote, len(voiceStream), measure, beat
                        )
                    )

                lastNote = note


def colorParts(piece):
    for voiceIndex in piece.voiceStreams:
        color = getVoiceColor(voiceIndex)

        voiceStream = piece.voiceStreams[voiceIndex]

        for note in voiceStream.recurse():
            if "isNote" in dir(note) and note.isNote:
                note.style.color = color
            elif "isRest" in dir(note) and note.isRest:
                note.style.color = 'black'


def colorFiguredBassNote(piece, voiceIndex, measure, note):
    note.style.color = "gold"

    if measure not in piece.figuredBassReports['counts']:
        piece.figuredBassReports['counts'][measure] = {}

    if voiceIndex not in piece.figuredBassReports['counts'][measure]:
        piece.figuredBassReports['counts'][measure][voiceIndex] = 0

    piece.figuredBassReports['counts'][measure][voiceIndex] += 1

    print(
        f"{measure} -> {note.name}"
    )


def handleFiguredBassNote(piece, voiceIndex, totalOffset, note, measure):
    if voiceIndex < 3:
        return

    figuredBassNote = getFiguredBassNote(piece, totalOffset)
    if note.isChord:
        for thisNote in note.notes:
            if thisNote.name == figuredBassNote:
                colorFiguredBassNote(piece, voiceIndex, measure, thisNote)

        return

    if note.name == figuredBassNote:
        colorFiguredBassNote(piece, voiceIndex, measure, note)


def getPaths(directory):
    paths = []

    for candidate in os.listdir(directory):
        if candidate.endswith(".musicxml") or candidate.endswith(".mxl") or candidate.endswith(".xml"):
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
            deltaString = deltaString + f"{delta.delta}{delta.note.nameWithOctave}, "

        print(deltaString)


def trimIndex(index):
    toDeletes = []
    for snippet in index.keys():
        if len(index[snippet]) < 2:
            toDeletes.append((snippet))

    for toDelete in toDeletes:
        index.pop(toDelete)

    for snippet in index.keys():
        index[snippet].sort(key=lambda x: (x['voice'], x['startingIndex']))




def formSyncedMidi(piece):
    if piece.movement.beatDurations == None or len(piece.movement.beatDurations) == 0:
        return

    goods = 0
    duds = 0

    totalNotes = {}
    totalSeconds = {}

    for candidate in piece.stream.recurse():
        if "isNote" in dir(candidate) or "isRest" in dir(candidate):
            offset = int(getOffset(piece, candidate))
            performanceBeatDuration = piece.movement.beatDurations[offset]

            try:
                beforeSeconds = candidate.seconds
                afterSeconds = performanceBeatDuration * candidate.duration.quarterLength

                if offset not in totalSeconds:
                    totalNotes[offset] = 0
                    totalSeconds[offset] = 0

                totalNotes[offset] += 1
                totalSeconds[offset] += afterSeconds

                candidate.seconds = afterSeconds
                print(f"seconds -> {beforeSeconds} -> {afterSeconds}")
                if "isRest" not in dir(candidate):
                    print(f"{offset} -> {candidate.nameWithOctave} -> {afterSeconds}")
                goods += 1
            except Music21Exception:
                candidate
                duds += 1

    totalDiff = 0
    totalBeatDurations = 0
    totalTotalSecodns = 0
    for i in range(0, len(piece.movement.beatDurations)):
        thisDiff = piece.movement.beatDurations[i] - totalSeconds[i] / 2
        totalBeatDurations += piece.movement.beatDurations[i]
        totalTotalSecodns += totalSeconds[i]
        totalDiff += thisDiff
        print(f"{i} {piece.movement.beatDurations[i]} -> {totalSeconds[i]} -> {thisDiff}")
    print(f"{totalDiff=}")
    duds


def writeSyncedMidi(piece):
    midiPath = getOutPath(piece.path, 'midi')
    fp = piece.stream.write("midi", fp=midiPath)
    print(f"{midiPath} was written")


def writeXml(piece):
    xmlPath = getOutPath(piece.path, 'musicxml')
    piece.stream.definesExplicitPageBreaks = False
    piece.stream.definesExplicitSystemBreaks = False
    fp = piece.stream.write("musicxml", fp=xmlPath)
    print(f"{xmlPath} was written")


def walkDirectory(directory):
    index = {}

    withDeltas = False
    writeBlack = False
    shouldColorFiguredBass = False
    shouldColorParts = True

    pieces = []
    for file in getPaths(directory):
        path = directory + "/" + file
        movement = pathToMovement(path)

        if not movement.name == 'Aria':
            continue

        print(f"{path} -> {movement.name}")
        piece = ingestFile(path)

        handlePartsVoices(piece)

        for voiceIndex in piece.voiceStreams:
            voiceStream = piece.getVoiceStream(voiceIndex)
            voiceNoteStream = piece.getVoiceNoteStream(voiceIndex)

            voiceStream.timeSignature = piece.stream.parts[0].measure(1).timeSignature
            voiceNoteStream.timeSignature = piece.stream.parts[0].measure(1).timeSignature

            # voiceStream.insert(0, metadata.Metadata())
            # voiceStream.metadata.movementName = f"voiceStream {voiceIndex=}"
            # voiceStream.show()
            #
            # voiceNoteStream.insert(0, metadata.Metadata())
            # voiceNoteStream.metadata.movementName = f"voiceNoteStream {voiceIndex=}"
            # voiceNoteStream.show()

        if withDeltas:
            indexDeltas(index, piece)

        pieces.append(piece)

    trimIndex(index)

    for piece in pieces:
        if writeBlack:
            path = piece.path.replace("musicxml-clean", "musicxml-out/black")
            fp = piece.stream.write("musicxml", fp=path)
            print(f"{path} was written")

        if shouldColorFiguredBass:
            colorFiguredBass(piece)
            # path = piece.path.replace("musicxml-clean", "musicxml-out/figured-bass")
            # fp = piece.stream.write("musicxml", fp=path)
            # print(f"{path} was written")

        if shouldColorParts:
            colorParts(piece)
            path = piece.path.replace("musicxml-clean", "musicxml-out/colored-parts")
            fp = piece.stream.write("musicxml", fp=path)
            print(f"{path} was written")

    for file in getPaths(directory):
        printDeltas(piece)
        handleDeltas(piece, index)
        # formSyncedMidi(piece)
        # writeSyncedMidi(piece)

        # versions
        # all black
        # all black - gold figured bass
        # colored voices - no extra figured bass colors
        # colored voices - colored figured bass
        # colored voice - colored figured bass - with lyrics for patterns

        writeXml(piece)


walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean")
