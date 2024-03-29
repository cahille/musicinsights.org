#!/usr/local/bin/python3.8
import copy
import json
import math
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

import music21
from music21 import *
from music21.exceptions21 import Music21Exception

from Delta import Delta
from Movement import Movement
from MusicHelper import MusicHelper
from MyNote import MyNote
from Piece import Piece

MARK_IN = articulations.StrongAccent()
MARK_OUT = articulations.Accent()
OFFSETS = {}
STATS = {
    'offsetsCount': {},
    'keys': {}
}
LEADER_COLOR = 'blue'
FOLLOWER_COLOR = 'green'


def computeMyKeys():
    myKeys = {}
    myKeysMap = {}

    for tonicOrdinal in range(49, 62):
        tonicNote = MyNote.getNote(tonicOrdinal)
        myKeys[f'{tonicNote} Major'] = []
        myKeys[f'{tonicNote} Minor'] = []

        myKeysMap[f'{tonicNote} Major'] = {}
        myKeysMap[f'{tonicNote} Minor'] = {}

        noteKeyIndex = 0
        totalOfset = 0
        for offset in (0, 2, 2, 1, 2, 2, 2):
            totalOfset += offset
            myKeys[MyNote.getNote(tonicOrdinal) + ' Major'].append((MyNote.getNote(tonicOrdinal + totalOfset)))
            myKeysMap[MyNote.getNote(tonicOrdinal) + ' Major'][MyNote.getNote(tonicOrdinal + totalOfset)] = noteKeyIndex
            noteKeyIndex += 1

        noteKeyIndex = 0
        totalOfset = 0
        for offset in (0, 2, 1, 2, 2, 1, 2):
            totalOfset += offset
            myKeys[MyNote.getNote(tonicOrdinal) + ' Minor'].append((MyNote.getNote(tonicOrdinal + totalOfset)))
            myKeysMap[MyNote.getNote(tonicOrdinal) + ' Minor'][MyNote.getNote(tonicOrdinal + totalOfset)] = noteKeyIndex
            noteKeyIndex += 1

    return myKeys, myKeysMap


MY_KEYS, MY_KEYS_MAP = computeMyKeys()

COMPOSE_OFFSETS = [
    [-1],
    [1],
    [-6],
    [6],
    [-1, 0],
    [1, 0],
    [-6, 0],
    [6, 0],
    [0, -1],
    [0, 1],
    [0, -6],
    [0, 6]
]

music21.environment.set("musescoreDirectPNGPath", "/Applications/MuseScore 3.app")
music21.environment.set("musicxmlPath", "/Applications/MuseScore 3.app")
music21.environment.set(
    "lilypondPath", "/Applications/LilyPond.app/Contents/Resources/bin/lilypond"
)

FIGURED_BASS_MEASURE_NOTE = {
    1: "G", 2: "F#", 3: "E", 4: "D", 5: "B", 6: "C", 7: "D", 8: "G", 9: "G", 10: "F#", 11: "E", 12: "A", 13: "F#", 14: "G", 15: "A", 16: "D",
    17: "D", 18: "B", 19: "C", 20: "B", 21: "G", 22: "A", 23: "D", 24: "C", 25: "C", 26: "B", 27: "A", 28: "D", 29: "G", 30: "C", 31: "D", 32: "G",
}
MINIMUM_SNIPPET_LENGTH = 10
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
    Movement('Variation 1', 32, False, {
        1: 1, 2: 4, 3: 4
    }),
    Movement('Variation 2', 32, True, {1: 1, 2: 2, 3: 4, 4: 4}),
    Movement('Variation 3', 16, False, {1: 1, 2: 2, 3: 3, 4: 3, 5: 3}, canonVoices=[1, 2], canonOffsetPositions=0),
    Movement('Variation 4', 32, True, {1: 1, 2: 2, 3: 3, 4: 4, 5: 4}, partOffsetMap={
        3: {3: [[22.5, 22.5], [49, 49.5]]},
        4: {3: [[7.5, 8.5], [15, 17.5], [25.5, 25.5], [51, 51]]}
    }),
    Movement('Variation 5', 32, False, {1: 1, 2: 4, 3: 4}),
    Movement('Variation 6', 32, True, {1: 1, 2: 2, 3: 3, 4: 3}, partOffsetMap={}, canonVoices=[2, 1], canonOffsetPositions=1),
    Movement('Variation 7', 32, False, {1: 1, 2: 2}),
    Movement('Variation 8', 32, False, {1: 1, 2: 2}),
    Movement('Variation 9', 16, False, {1: 1, 2: 2, 3: 3, 4: 3}, canonVoices=[1, 2], canonOffsetPositions=-2),
    Movement('Variation 10', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4}, partOffsetMap={
        3: {3: [[16, 38], [44, 62], [112, 126]]},
        4: {3: [[24, 27], [32, 34], [40, 42]]}
    }),
    Movement('Variation 11', 32, False, {1: 1, 2: 2, 3: 2, 4: 2}),
    Movement('Variation 12', 32, False, {1: 1, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3}, partOffsetMap={
        4: {3: [[39, 42], [45, 47], [60.5, 83.75]]},
        5: {2: [[9.5, 10.25]]},
    }, canonVoices=[1, 2], canonOffsetPositions=-3, canonInverted=True),
    Movement('Variation 13', 32, False, {1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4}, partOffsetMap={
        4: {2: [[13, 13]]}
    }),
    Movement('Variation 14', 32, False, {1: 1, 2: 2}),
    Movement('Variation 15', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}, partOffsetMap={
        # 4: {2: [[4, 7.25], [12, 13.875], [24.5, 27.25], [28.5, 29.75], [52, 53.5], [60, 62]]},
        # 5: {2: [[14, 14], [54, 54.5]]}
    }, canonVoices=[1, 2], canonOffsetPositions=-7, canonInverted=True),  # G, A-flat, A, B-flat, B, C, C-sharp, D
    Movement('Variation 16', 48, True, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4, 6: 4}, partOffsetMap={
        3: {3: [[117.5, 117.5]]},
        4: {3: [[0, 0], [3.75, 4], [53.75, 54]]}
    }),
    Movement('Variation 17', 32, False, {1: 1, 2: 2}),
    Movement('Variation 18', 32, False, {1: 1, 2: 2, 3: 3, 4: 3, 5: 3}, canonVoices=[2, 1], canonOffsetPositions=8, canonInverted=True),
    # G, A-flat, A, B-flat, B, C, C-sharp, D),  # B, C, C-sharp, D, D-sharp, E, F, F-sharp, G
    Movement('Variation 19', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}, partOffsetMap={
        4: {2: [[24, 24.5], [42, 47]]},
        5: {2: [[25.5, 25.5]]}
    }),
    Movement('Variation 20', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}),
    Movement('Variation 21', 16, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 3}, partOffsetMap={
        4: {2: [[0, 7.5], [20, 23.5], [60.75, 62]]},
        5: {2: [[43, 45], [48.25, 49.75]]},
    }, canonOffsetPositions=11),  # B-flat, B, C, D-flat, D, E-flat, E, F, G-flat, G, A-flat, A
    Movement('Variation 22', 32, False, {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4}, partOffsetMap={
        # 3: {3: [[34, 44], [50, 60], [78, 92], [98, 104], [112, 112]],
        #     4: [[68, 75], [96, 103]]},
        3: {3: [[34, 44], [50, 60], [78, 78], [84, 92], [106, 111], [116, 124]],
            4: [[68, 75], [96, 103]]},  # , [64, 112], [116, 124]]},
        4: {4: [[32, 56], [64, 110], [116, 118], [124, 124]]},  # , [64, 112], [116, 124]]}, 2, 4, -5,
        5: {3: [[80, 83]]},
    }),
    Movement('Variation 23', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4}, partOffsetMap={
        3: {3: [[54.25, 57.5]]},
        4: {3: [[73.25, 95], [48.25, 51.5]]},
    }),
    Movement('Variation 24', 32, False, {1: 1, 2: 2, 3: 4, 4: 4, 5: 4, 6: 4}, partOffsetMap={
        1: {2: [[36, 44.5]]},
        3: {2: [[15, 17.5]]},
        4: {2: [[9, 13], [45, 51], [63, 66], [63, 95.5], [117, 121], [126.5, 143]]},
        5: {2: [[13.5, 13.5], [14.5, 14.5], [54, 56.5], [67.5, 67.5], [122, 124.5]]},
        6: {4: [[54, 58]]}
    }, canonOffsetPositions=12),  # not really on canonOffsetPositions
    Movement('Variation 25', 32, True, {1: 1, 2: 3, 3: 4, 4: 3, 5: 4}),
    # Movement('Variation 26', 32, False, {1: 1, 2: 2, 3: 4, 4: 3, 5: 3, 6: 4}),
    Movement('Variation 27', 32, False, {1: 1, 2: 2, 3: 4, 4: 3, 5: 3, 6: 4}, canonOffsetPositions=14),  # G, A-flat, A, B-flat, B, C, D-flat, D, E-flat, E, F, G-flat, G, G-flat, A
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
    stream = converter.parse(path, forceSource=True)
    stream.insert(0, metadata.Metadata())
    stream.metadata.composer = "Johann Sebastian Bach"
    stream.metadata.movementName = pathToMovement(path).name

    return stream


def snippetToString(snippet):
    return ",".join(map(lambda delta: str(delta.delta), snippet))


def getKeyCandidates(snippet):
    keyCandidates = {}
    for key in MY_KEYS:
        for snip in snippet:
            note = MyNote.getNote(MyNote.getNoteOrdinal(snip.note))
            if note in MY_KEYS_MAP[key]:
                if key not in keyCandidates:
                    keyCandidates[key] = 0
                keyCandidates[key] += 1

    return keyCandidates


def indexDeltas(chromaticIndex, scalarIndex, piece):
    if piece.movement.name == 'Aria da capo':
        return

    for voice in piece.deltas.keys():
        chromaticDeltas = piece.deltas[voice]['chromatic']
        scalarDeltas = piece.deltas[voice]['scalar']

        for i in range(0, len(chromaticDeltas) - MINIMUM_SNIPPET_LENGTH):
            snippet = chromaticDeltas[i: i + MINIMUM_SNIPPET_LENGTH]
            snippetString = snippetToString(snippet)
            if not snippetString in chromaticIndex:
                chromaticIndex[snippetString] = []

            chromaticIndex[snippetString].append(
                {
                    'piece': piece,
                    'startingIndex': i,
                    'snippet': snippet,
                    'voice': voice,
                }
            )

            keyCandidates = getKeyCandidates(snippet)


def beatInt(beat):
    pair = str(beat).split('/')
    if len(pair) == 1:
        return int(float(pair[0]))
    else:
        return int(float(pair[0]) / float(pair[1]))


def matchIncluded(matched, matchCandidate):
    for match in matched:
        if matchCandidate['piece'].movement.name != match['piece'].movement.name or matchCandidate['voice'] != match['voice']:
            continue

        if match['i'] <= matchCandidate['startingIndex'] and match['j'] >= matchCandidate['startingIndex']:
            return True

    return False


def handleDeltas(piece, index):
    matches = {}
    matched = []

    for snippet in index.keys():
        for i in range(0, len(index[snippet])):
            main = index[snippet][i]
            mainVoice = index[snippet][i]['voice']
            mainStream = main['piece'].getVoiceNoteArray(mainVoice)

            if matchIncluded(matched, main):
                continue

            for deltaIndex in range(1, len(index[snippet])):
                child = index[snippet][deltaIndex]

                # if child['piece'].movement != main['piece'].movement:
                #     child

                if matchIncluded(matched, child):
                    continue

                childStream = child['piece'].voiceNoteArrays[child['voice']]

                mainStartingLoopIndex = main['startingIndex'] + MINIMUM_SNIPPET_LENGTH
                childStartingLoopIndex = child['startingIndex'] + MINIMUM_SNIPPET_LENGTH
                mainLastNote = mainStream[mainStartingLoopIndex - 1]
                childLastNote = childStream[childStartingLoopIndex - 1]

                for lookAhead in range(0, len(mainStream) - mainStartingLoopIndex):
                    # print(f"    lookahead - {lookAhead}")

                    thisMainIndex = mainStartingLoopIndex + lookAhead
                    thisChildIndex = childStartingLoopIndex + lookAhead

                    mainNote = mainStream[thisMainIndex]
                    childNote = childStream[thisChildIndex]

                    # print(f"mainNote: {mainNote.nameWithOctave}")
                    # print(f"childNote: {childNote.nameWithOctave}")

                    if ((thisMainIndex + 1) == len(mainStream)) or ((thisChildIndex + 1) == len(childStream)) \
                            or (
                            (MyNote.getNoteOrdinal(mainNote) - MyNote.getNoteOrdinal(mainLastNote)) != (
                            MyNote.getNoteOrdinal(childNote) - MyNote.getNoteOrdinal(childLastNote))):
                        matchCandidateOne = {'piece': main['piece'], 'voice': mainVoice, 'i': mainStartingLoopIndex, 'j': thisMainIndex - 1}
                        matchCandidateTwo = {'piece': child['piece'], 'voice': child['voice'], 'i': child['startingIndex'], 'j': thisChildIndex - 1}

                        matched.append(matchCandidateOne)
                        matched.append(matchCandidateTwo)

                        matchLength = MINIMUM_SNIPPET_LENGTH + lookAhead + 1

                        # the -1 for endnotes is because this note didn't match
                        mainStartNote = mainStream[main['startingIndex']]
                        childStartNote = childStream[child['startingIndex']]

                        if ((thisMainIndex + 1) == len(mainStream)) or ((thisChildIndex + 1) == len(childStream)):
                            mainEndNote = mainStream[thisMainIndex]
                            childEndNote = childStream[thisChildIndex]
                        else:
                            mainEndNote = mainStream[thisMainIndex - 1]
                            childEndNote = childStream[thisChildIndex - 1]

                        mainPart = f"v{mainVoice} {getMeasureBeatString(main['piece'], mainStartNote)}-" + f"{getMeasureBeatString(main['piece'], mainEndNote)}"
                        childPart = f"v{child['voice']} {getMeasureBeatString(child['piece'], childStartNote)}" + f"-{getMeasureBeatString(child['piece'], childEndNote)}"

                        if childPart in matches:
                            matchLetter = matches[childPart]['letter']
                            matchLength = matches[childPart]['length']
                        elif mainPart in matches:
                            matchLetter = matches[mainPart]['letter']
                            matchLength = matches[mainPart]['length']
                        else:
                            # matchLetter = chr(ord('@') + int(len(matches) / 2) + 1)
                            matchLetter = len(matches) + 1
                            thisMatch = {'letter': matchLetter, 'length': matchLength}
                            matches[mainPart] = thisMatch
                            matches[childPart] = thisMatch

                        addLyrics = True
                        if addLyrics:
                            movementReference = ''
                            if child['piece'].movement != main['piece'].movement:
                                movementReference = f"{child['piece'].movement.name}: "

                        if addLyrics:
                            mainLyric = f"[{matchLetter}: {matchLength} " + \
                                        f"{mainPart}"
                            mainLyric += ", " + f"{movementReference}{childPart}"

                            if mainStartNote.lyric == None or not mainLyric in mainStartNote.lyric:
                                if mainEndNote.articulations == None or (len(mainEndNote.articulations) == 0) or (
                                        len(mainEndNote.articulations) > 0 and mainEndNote.articulations[0] == MARK_OUT):
                                    mainStartNote.articulations.append(MARK_IN)
                                mainStartNote.addLyric(mainLyric)

                            mainEndString = f"v{mainVoice} {matchLetter}]"
                            if mainEndNote.lyric == None or not mainEndString in mainEndNote.lyric:
                                mainEndNote.addLyric(mainEndString)
                                if mainEndNote.articulations == None or (len(mainEndNote.articulations) == 0) or (
                                        len(mainEndNote.articulations) > 0 and mainEndNote.articulations[0] == MARK_IN):
                                    mainEndNote.articulations.append(MARK_OUT)

                            childLyric = f"[{matchLetter}: {matchLength} " + \
                                         f"{childPart}"
                            childLyric += ", " + f"{movementReference}{mainPart}"

                            if childStartNote.lyric == None or not childLyric in childStartNote.lyric:
                                if childStartNote.articulations == None or (len(childStartNote.articulations) == 0) or (
                                        len(childStartNote.articulations) > 0 and childStartNote.articulations[0] == MARK_OUT):
                                    childStartNote.articulations.append(MARK_IN)
                                childStartNote.addLyric(childLyric)

                            childEndString = f"v{child['voice']} {matchLetter}]"
                            if childEndNote.lyric == None or not childEndString in childEndNote.lyric:
                                childEndNote.addLyric(childEndString)
                                if childEndNote.articulations == None or (len(childEndNote.articulations) == 0) or (
                                        len(childEndNote.articulations) > 0 and childEndNote.articulations[0] == MARK_IN):
                                    childEndNote.articulations.append(MARK_OUT)

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
    if piece in OFFSETS and note.id in OFFSETS[piece]:
        return OFFSETS[piece][note.id]

    offset = None
    for candidate in piece.stream.flat:
        if candidate.id == note.id:
            offset = candidate.getOffsetBySite(piece.stream.flat)
            break
        elif "isChord" in dir(candidate) and candidate.isChord:
            for subCandidate in candidate.notes:
                if subCandidate.id == note.id:
                    offset = candidate.getOffsetBySite(piece.stream.flat)
                    break

    if offset != None:
        if piece not in OFFSETS:
            OFFSETS[piece] = {}

        OFFSETS[piece][note.id] = offset

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

    for element in thisStream.flat:
        if "isNote" in dir(element) or "isRest" in dir(element) or isinstance(element, music21.text.TextBox) or isinstance(element, music21.expressions.TextExpression):
            continue
        if isinstance(element, music21.instrument.Instrument):
            thisStream.remove(element)
            continue
        if isinstance(element, music21.layout.SystemLayout) and element.measureNumber > 0:
            thisStream.remove(element)
            continue

    # setting time signatures to all parts to the time signature of the 0th
    for i in range(1, len(thisStream.parts)):
        if not thisStream.parts[i].timeSignature:
            thisStream.parts[i].timeSignature = thisStream.parts[0].measure(1).timeSignature

    piece = Piece(path, movement, thisStream)

    return piece


def letsCompose(piece):
    partNumber = 0

    masterStream = stream.Stream()

    for part in piece.stream.voicesToParts():
        if not hasNote(part):
            continue

        thisPart = music21.stream.Part()
        thisPart.timeSignature = part.measure(1).timeSignature

        partNumber = partNumber + 1

        for note in part.recurse():
            if "isRest" not in dir(note) and "isNote" not in dir(note):
                continue

            if note.isRest:
                thisPart.append(note)
                continue

            if note.tie:
                thisPart.append(note)
                continue

            totalOffset = note.getOffsetInHierarchy(piece.stream)
            voiceIndex = getVoiceIndex(piece.movement, partNumber, totalOffset)
            measure, beat = getMeasureBeat(piece, totalOffset)

            if voiceIndex == 1:
                thisPart.append(note)
                continue

            theseOffsets = random.choice(COMPOSE_OFFSETS)

            offsets = len(theseOffsets)

            for thisOffset in theseOffsets:
                newNote = music21.note.Note(note.nameWithOctave)
                newNote.nameWithOctave = MyNote.getNoteWithOctave(MyNote.getNoteOrdinal(newNote) + thisOffset)
                newNote.duration.quarterLength = note.duration.quarterLength / offsets
                thisPart.append(newNote)

        masterStream.append(thisPart)

    piece.stream = masterStream


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


def handlePartsVoices(piece, generateStats=False):
    partNumber = 0

    voiceOffsetMap = {}

    for topPart in piece.stream.parts:
        for part in topPart.voicesToParts():
            if not hasNote(part):
                continue

            partNumber += 1

            part.insert(0, metadata.Metadata())
            part.metadata.movementName = f"{part.id=}, {partNumber=}"
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
                        print(f"offset overlap p{partNumber} -> v{voiceIndex} -> {totalOffset}")

                voiceOffsetMap[voiceIndex][totalOffset] = note

    for voiceIndex in voiceOffsetMap.keys():
        lastNote = None

        voiceArray = piece.getVoiceArray(voiceIndex)
        voiceNoteArray = piece.getVoiceNoteArray(voiceIndex)

        for totalOffset, note in sorted(voiceOffsetMap[voiceIndex].items()):
            if "isRest" not in dir(note) and "isNote" not in dir(note) and "isChord" not in dir(note):
                continue

            voiceArray.append(note)

            if "isRest" in dir(note) and note.isRest:
                continue

            if "isNote" in dir(note) and note.isNote:
                pieceVoice = piece.getVoice(voiceIndex)
                pieceDeltas = piece.getDeltas(voiceIndex)

                if note.tie and note.tie.type != 'start':
                    continue

                voiceNoteArray.append(note)

                measure, beat = getMeasureBeat(piece, totalOffset)
                myNote = MyNote(note)

                print(
                    f"v{voiceIndex} -> {measure} -> {beat} -> {totalOffset} -> {note.nameWithOctave} -> {myNote.noteOrdinal}"
                )

                pieceVoice.append(myNote)
                if lastNote:
                    pieceDeltas['chromatic'].append(
                        Delta(
                            myNote.noteOrdinal - pieceVoice[len(pieceVoice) - 2].noteOrdinal, lastNote, len(voiceArray), measure, beat
                        )
                    )

                lastNote = note

    for voiceIndex in piece.voiceArrays:
        myShow(piece.stream.parts[0].measure(1).timeSignature, piece.voiceArrays[voiceIndex], f"{piece.movement.name}: {voiceIndex}")

    if generateStats:
        for key in STATS:
            if piece.movement.name not in STATS[key]:
                STATS[key][piece.movement.name] = {}

        for voiceIndex in voiceOffsetMap.keys():
            for totalOffset, note in sorted(voiceOffsetMap[voiceIndex].items()):
                intTotalOffset = int(totalOffset) + 1
                if intTotalOffset not in STATS['offsetsCount'][piece.movement.name]:
                    STATS['offsetsCount'][piece.movement.name][intTotalOffset] = 0

                STATS['offsetsCount'][piece.movement.name][intTotalOffset] += 1

        STATS['keys'][piece.movement.name] = getKeyStats(piece.stream)


def getKeyStats(stream):
    ksAnalyzer = analysis.discrete.KrumhanslSchmuckler()
    windowedAnalysis = analysis.windowed.WindowedAnalysis(stream, ksAnalyzer)
    theseKeys, ignore = windowedAnalysis.analyze(1)

    keys = []

    for key in theseKeys:
        keys.append(None if key == None else {
            'name': None if key[0] == None else key[0].name,
            'flavor': key[1],
            'number': key[2]
        })

    return keys


def generateGenericStats(path):
    stream = converter.parse(path, forceSource=True)
    # stream.show()
    stats = {
        'histogram': {
            'values': {
                'global': {},
                'note': {}
            },
            'global': {},
            'note': {}
        },
        'offsetsCount': {
        }
    }

    for element in stream.flat:
        if "isNote" in dir(element) and element.isNote:
            offset = element.getOffsetInHierarchy(stream)

            if offset not in stats['offsetsCount']:
                stats['offsetsCount'][offset] = 0

            stats['offsetsCount'][offset] += 1

            for (type, value) in (
                    ('note', element.name),
                    ('global', MyNote.getNoteOrdinal(element))):
                beatOffset = offset + 1
                if beatOffset not in stats['histogram'][type]:
                    stats['histogram'][type][beatOffset] = {}

                if element.name not in stats['histogram'][type][beatOffset]:
                    stats['histogram'][type][beatOffset][value] = 0

                stats['histogram'][type][beatOffset][value] += 1

                if value not in stats['histogram']['values'][type]:
                    stats['histogram']['values'][type][value] = 1
                else:
                    stats['histogram']['values'][type][value] += 1

    stats['keys'] = getKeyStats(stream)
    stats['scoreTimings'] = getScoreTimings(stream, stats['offsetsCount'])

    with open(os.path.dirname(path) + '/stats.json', 'w') as statsFile:
        print(f"writing to {statsFile}")
        json.dump(stats, statsFile, indent=4)


def getCurrentMetronome(metronomeOffsets, offset):
    if offset in metronomeOffsets:
        return metronomeOffsets[offset]

    lastMetronome = None
    for thisOffset, metronome in sorted(metronomeOffsets.items()):
        if thisOffset > offset:
            return lastMetronome

        lastMetronome = metronome

    return lastMetronome


def getScoreTimings(stream, offsets):
    metronomeOffsets = getMetronomeOffsets(stream)

    maxOffset = sorted(offsets.keys(), reverse=True)[0]

    for offset in range(0, math.ceil(maxOffset)):
        if float(offset) not in offsets:
            offsets[float(offset)] = 0

    if len(metronomeOffsets) != 1:
        print(f'need to have 1 metronomeOffsets :( {len(metronomeOffsets)} - {metronomeOffsets}')

    scoreTimings = []

    for offset in sorted(offsets.keys()):
        beat = offset + 1

        currentMetronome = getCurrentMetronome(metronomeOffsets, offset)

        if currentMetronome == None:
            print("darn no currentMetronome")
        elif currentMetronome.beatDuration.type == 'quarter':
            scoreTimings.append({
                'offset': offset,
                'beat': beat,
                'elapsed': beat * (60 / currentMetronome.number)
            })
        else:
            print("darn no quarter given")

    return scoreTimings


def getMetronomeOffsets(stream):
    metronomeOffsets = {}

    for part in stream.parts:
        for element in part.flat:
            if isinstance(element, music21.tempo.MetronomeMark):
                offset = element.getOffsetInHierarchy(stream)
                if offset not in metronomeOffsets:
                    metronomeOffsets[offset] = element
                elif metronomeOffsets[offset].number == element.number:
                    print(f"kind of redundant metronome marking {element}")
                else:
                    metronomeOffsets[offset] = element
                    print(f"lots of metronome markings! {element}")

    return metronomeOffsets


def colorParts(piece):
    for voiceIndex in piece.voiceArrays:
        color = getVoiceColor(voiceIndex)

        voiceArray = piece.getVoiceArray(voiceIndex)

        # myShow(voiceArray)

        for note in voiceArray:
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
    if not voiceIndex or voiceIndex < 3:
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
    for voiceIndex in piece.voiceNoteArrays:
        noteWithOctaveString = f"   {voiceIndex} -> "
        noteOrdinalString = f"   {voiceIndex} -> "
        for note in piece.getVoiceNoteArray(voiceIndex):
            if ("nameWithOctave" in dir(note)):
                noteWithOctaveString = noteWithOctaveString + f"{note.nameWithOctave}, "
                noteOrdinalString = noteOrdinalString + f"{MyNote.getNoteOrdinal(note)}, "

        print(noteWithOctaveString)
        print(noteOrdinalString)

    print("deltas")
    for voiceIndex in piece.deltas:
        deltaString = f"   {voiceIndex} -> "
        for delta in piece.deltas[voiceIndex]['chromatic']:
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


def getLeaderFollowerInfo(movement, piece):
    leader = piece.voiceArrays[movement.canonVoices[0]]
    follower = piece.voiceArrays[movement.canonVoices[1]]

    leaderFirstHalf = 0
    leaderSecondHalf = 0
    followerFirstHalf = 0
    followerSecondHalf = 0
    followerFirstHalfLag = None
    followerSecondHalfLag = None
    leaderOffsets = {}
    leaderInitialSecondHalfOffset = None

    halfMeasures = movement.measures / 2

    for i in range(0, len(leader)):
        leaderOffset = getOffset(piece, leader[i])
        leaderOffsets[leaderOffset] = leader[i]

        measure, beat = getMeasureBeat(piece, leaderOffset)
        if measure <= halfMeasures:
            leaderFirstHalf += 1
        else:
            leaderSecondHalf += 1
            if not leaderInitialSecondHalfOffset:
                leaderInitialSecondHalfOffset = leaderOffset

    for i in range(0, len(follower)):
        followerNote = follower[i]

        measure, beat = getMeasureBeat(piece, getOffset(piece, followerNote))

        if measure <= halfMeasures:
            followerFirstHalf += 1
            if followerFirstHalfLag == None:
                followerFirstHalfLag = getOffset(piece, followerNote)
        else:
            followerSecondHalf += 1
            if followerSecondHalfLag == None:
                followerSecondHalfLag = getOffset(piece, followerNote) - leaderInitialSecondHalfOffset

    followerFirstHalfDuration = getOffset(piece, follower[followerFirstHalf - 1]) + follower[followerFirstHalf - 1].duration.quarterLength - getOffset(piece, follower[0])
    followerSecondHalfDuration = getOffset(piece, follower[-1]) - getOffset(piece, follower[followerFirstHalf])

    return {
        'leader': leader,
        'follower': follower,
        'leaderCounts': [leaderFirstHalf, leaderSecondHalf],
        'followerCounts': [followerFirstHalf, followerSecondHalf],
        'followerDuration': [followerFirstHalfDuration, followerSecondHalfDuration],
        'followerLag': [followerFirstHalfLag, followerSecondHalfLag],
        'leaderOffsets': leaderOffsets
    }


def getLeaderNote(piece, leaderFollowerInfo, offset):
    if offset < piece.movement.measures / 2 * piece.getBeatsPerMeasure():
        lag = getOffset(piece, leaderFollowerInfo['follower'][0]) - getOffset(piece, leaderFollowerInfo['leader'][0])
    else:
        lag = leaderFollowerInfo['followerLag'][1]

    leaderOffset = offset - lag

    if leaderOffset in leaderFollowerInfo['leaderOffsets']:
        return leaderFollowerInfo['leaderOffsets'][leaderOffset]

    lastNote = None

    for (thisOffset, note) in sorted(leaderFollowerInfo['leaderOffsets'].items()):
        if leaderOffset >= thisOffset and leaderOffset <= (thisOffset + note.duration.quarterLength):
            return note

        if thisOffset > leaderOffset:
            return lastNote

        lastNote = note

    return None


def handleLeader(movement, piece, leaderFollowerInfo):
    leader = leaderFollowerInfo['leader']

    toRemove = []

    halfMeasure = movement.measures / 2
    beatsPerMeasure = piece.getBeatsPerMeasure()

    for i in range(0, len(leader)):
        if i > leaderFollowerInfo['followerCounts'][0] and i <= leaderFollowerInfo['leaderCounts'][0]:
            measure, beat = getMeasureBeat(piece, getOffset(piece, leader[i]))

            if measure <= halfMeasure:
                # leader[i].style.color = '#B0E0E6'
                leader[i].style.color = 'gray'
                toRemove.append(i)
                continue
            else:
                print()

        leaderNote = leader[i]
        leaderOffset = getOffset(piece, leaderNote)
        if leaderOffset > ((movement.measures * beatsPerMeasure) - leaderFollowerInfo['followerLag'][1] - 1):
            leaderNote.style.color = 'gray'
            toRemove.append(i)
            continue

        leader[i].style.color = LEADER_COLOR

    toRemove.reverse()
    for i in toRemove:
        del leader[i]


def handleCanonWalk(movement, piece):
    if movement.canonVoices is None or len(movement.canonVoices) == 0:
        return

    leaderFollowerInfo = getLeaderFollowerInfo(movement, piece)
    handleLeader(movement, piece, leaderFollowerInfo)

    leader = leaderFollowerInfo['leader']
    follower = leaderFollowerInfo['follower']

    myShow(piece.stream.parts[0].measure(1).timeSignature, leader, "leader for " + movement.name)
    myShow(piece.stream.parts[0].measure(1).timeSignature, follower, "follower for " + movement.name)

    canonOffsetPositions = movement.canonOffsetPositions
    inverted = movement.canonInverted if movement.canonInverted else False

    greenFollowers = 0
    redFollowers = 0

    for i in range(0, len(follower)):
        followerNote = follower[i]
        leaderNote = getLeaderNote(piece, leaderFollowerInfo, getOffset(piece, followerNote))
        predictedOrdinal = None

        sharpLeaderNote = None
        naturalLeaderNote = None
        flatLeaderNote = None
        predictorNote = None

        if leaderNote:
            if leaderNote.name != 'F#' and leaderNote.pitch.accidental:
                if leaderNote.pitch.accidental.name == 'sharp':
                    sharpLeaderNote = True
                elif leaderNote.pitch.accidental.name == 'natural':
                    naturalLeaderNote = True
                elif leaderNote.pitch.accidental.name == 'flat':
                    flatLeaderNote = True
                else:
                    leaderNote

            if sharpLeaderNote:
                predictorNote = music21.note.Note(MyNote.getNoteWithOctave(MyNote.getNoteOrdinal(leaderNote) - 1))
            elif naturalLeaderNote:
                predictorNote = music21.note.Note(MyNote.getNoteWithOctave(MyNote.getNoteOrdinal(leaderNote) + 1))
            else:
                predictorNote = leaderNote

            if inverted:
                thisDiff = MusicHelper.keyNoteDiff(key.Key('G'), music21.note.Note(MyNote.getNoteWithOctave(47)), predictorNote)
                if thisDiff is not None:
                    thisDiff *= -1
                    thisOrdinal = MusicHelper.shiftNote(key.Key('G'), music21.note.Note(MyNote.getNoteWithOctave(47)), canonOffsetPositions)
                    if thisOrdinal:
                        shiftedNote = music21.note.Note(MyNote.getNoteWithOctave(thisOrdinal))
                        predictedOrdinal = MusicHelper.shiftNote(key.Key('G'), shiftedNote, thisDiff)

            else:
                predictedOrdinal = MusicHelper.shiftNote(key.Key('G'), predictorNote, canonOffsetPositions)
        if not predictedOrdinal:
            follower[i].style.color = 'red'
            redFollowers += 1
            follower[i].addLyric('?')
            continue
        else:
            if sharpLeaderNote:
                predictedOrdinal += 1
            elif naturalLeaderNote or flatLeaderNote:
                predictedOrdinal -= 1

            predictedOrdinal

        if MyNote.getNoteOrdinal(followerNote) == predictedOrdinal:
            follower[i].style.color = FOLLOWER_COLOR
            greenFollowers += 1
        else:
            follower[i].style.color = 'red'
            redFollowers += 1
            follower[i].addLyric('X')

    print(f'{greenFollowers=}, {redFollowers=}')
    handleWrite(piece, "canons-colored")


def myShow(timeSignature, array, message=None):
    stream = music21.stream.Stream()
    stream.timeSignature = timeSignature

    for note in array:
        stream.append(note)

    if message is not None:
        stream.insert(0, metadata.Metadata())
        stream.metadata.movementName = message

    # stream.show()


def handleWrite(piece, place, open=False):
    myPiece = copy.deepcopy(piece)

    path = myPiece.path.replace("musicxml-clean", f"musicxml-out/{place}")
    fp = myPiece.stream.write("musicxml", fp=path)
    print(f"{path} was written")

    if open:
        os.system(f'open "{path}" &')


def walkDirectory(directory, thisMovement=None, movementLimit=None, movements=None, canonWalk=False,
                  withInsights=False, writeBlack=False, shouldColorFiguredBass=False, shouldColorParts=False, generateStats=False, compose=False):
    chormaticIndex = {}
    scalarIndex = {}

    matchedMovements = []
    pieces = []
    for file in getPaths(directory):
        path = directory + "/" + file
        movement = pathToMovement(path)

        if thisMovement != None and movement.name != thisMovement:
            continue

        if movements != None and movement.name not in movements:
            continue

        print(f"{path} -> {movement.name}")
        piece = ingestFile(path)

        handlePartsVoices(piece, generateStats)

        # for voiceIndex in piece.voiceArrays:
        #     voiceArray = piece.getVoiceArray(voiceIndex)
        #     voiceNoteArray = piece.getVoiceNoteArray(voiceIndex)
        #
        #     voiceArray.timeSignature = piece.stream.parts[0].measure(1).timeSignature
        #     voiceNoteArray.timeSignature = piece.stream.parts[0].measure(1).timeSignature
        #
        #     voiceArray.insert(0, metadata.Metadata())
        #     voiceArray.metadata.movementName = f"voiceArray {voiceIndex=}"
        #     voiceArray.show()
        #
        #     voiceNoteArray.insert(0, metadata.Metadata())
        #     voiceNoteArray.metadata.movementName = f"voiceNoteArray {voiceIndex=}"
        #     voiceNoteArray.show()

        if withInsights:
            indexDeltas(chormaticIndex, scalarIndex, piece)

        matchedMovements.append(movement)
        pieces.append(piece)

        if movementLimit != None and len(pieces) >= movementLimit:
            break

    trimIndex(chormaticIndex)

    for piece in pieces:
        if writeBlack:
            handleWrite(piece, "black")

    for piece in pieces:
        myPiece = copy.deepcopy(piece)

        if compose:
            letsCompose(myPiece)

            path = myPiece.path.replace("musicxml-clean", "musicxml-out/composed").replace(".musicxml", datetime.now().strftime(" %Y-%m-%d-%H-%M-%S") + ".musicxml")
            fp = myPiece.stream.write("musicxml", fp=path)
            print(f"{path} was written")

    for piece in pieces:
        myPiece = copy.deepcopy(piece)

        if shouldColorFiguredBass:
            colorFiguredBass(myPiece)
            # myPiece.backInBlack()
            path = myPiece.path.replace("musicxml-clean", "musicxml-out/figured-bass")
            fp = myPiece.stream.write("musicxml", fp=path)
            path = path.replace('.musicxml', '.xml')
            os.system(f'open "{path}" &')
            print(f"{path} was written")

    for piece in pieces:
        myPiece = copy.deepcopy(piece)

        if shouldColorParts:
            colorParts(myPiece)
            handleWrite(myPiece, "colored-parts")

    for piece in pieces:
        myPiece = copy.deepcopy(myPiece)

        if shouldColorFiguredBass and shouldColorParts:
            colorFiguredBass(piece)
            path = myPiece.path.replace("musicxml-clean", "musicxml-out/colored-parts-and-figured-bass")
            fp = myPiece.stream.write("musicxml", fp=path)
            path = path.replace('.musicxml', '.xml')
            os.system(f'open "{path}" &')
            print(f"{path} was written")

    if canonWalk:
        for i in range(0, len(pieces)):
            movement = matchedMovements[i]

            if movement.canonVoices is None or len(movement.canonVoices) == 0:
                continue

            myPiece = copy.deepcopy(pieces[i])

            handleCanonWalk(movement, myPiece)
        # versions
        # all black
        # all black - gold figured bass
        # colored voices - no extra figured bass colors
        # colored voices - colored figured bass
        # colored voice - colored figured bass - with lyrics for patterns

    if generateStats:
        # with open('/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations' + '/stats.json', 'w') as statsFile:
        with open(directory + '/stats.json', 'w') as statsFile:
            json.dump(STATS, statsFile, indent=4)


# generateGenericStats('/Users/earlcahill/music-video-experiments/transcendental_etude_no_10/transcendental_etude_no_10.musicxml')
# generateGenericStats('/Users/earlcahill/music-video-experiments/transcendental_etude_no_10/transcendental_etude_no_10.musicxml')
# walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean", movements=["Variation 1"], writeBlack=True, shouldColorParts=True)
# walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean", movements=["Aria"], generateStats=True)
# generateGenericStats('/Users/earlcahill/music-video-experiments/goldbergs/01-Aria/01-Aria.musicxml')

walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean", "Variation 10", withInsights=False, writeBlack=True,
              shouldColorFiguredBass=False, shouldColorParts=True, canonWalk=True)

# walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean", "Aria", canonWalk=False, withInsights=False, writeBlack=True,
#               shouldColorFiguredBass=False, shouldColorParts=False, compose=False)

# walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean", movementLimit=1, generateStats=True)
# walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean", shouldColorFiguredBass=True)
# walkDirectory("/Users/earlcahill/Downloads", movements=['feux follets'], generateStats=True)
# walkDirectory("/Users/earlcahill/dev/musicinsights.org-corpus/GoldbergVariations/musicxml-clean", withInsights=True, writeBlack=True, shouldColorFiguredBass=True,
#               shouldColorParts=True)


# Measure 21, staff 1 incomplete. Expected: 5/8; Found: 124/192
# Measure 76, staff 1 incomplete. Expected: 35/64; Found: 109/192
# Measure 78, staff 1 incomplete. Expected: 43/64; Found: 137/192
# Measure 79, staff 1 incomplete. Expected: 43/64; Found: 137/192
# Measure 87, staff 1 incomplete. Expected: 5/8; Found: 124/192
# Measure 143, staff 2 incomplete. Expected: 35/64; Found: 109/192
# Measure 145, staff 2 incomplete. Expected: 35/64; Found: 109/192