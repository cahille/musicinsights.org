from music21 import key

from MyNote import MyNote


class MusicHelper:
    @staticmethod
    def setKeyNotes():
        minOrdinal = 4
        maxOrdinal = 88

        noteOffsets = range(-14, 15)
        keyNotes = {}
        keyNoteLookup = {}

        for thisKey in [key.Key('G')]:
            keyNotes[thisKey] = {}
            keyNoteLookup[thisKey] = {}
            for ordinal in range(minOrdinal, 24):
                startNote = MyNote.getNote(ordinal)
                if startNote == thisKey.tonic.name:
                    keyNoteOrdinals = [ordinal]
                    notes = [startNote]

                    while ordinal < maxOrdinal:
                        for offset in (2, 2, 1, 2, 2, 2, 1):
                            ordinal += offset
                            if ordinal > maxOrdinal:
                                break

                            keyNoteOrdinals.append(ordinal)
                            notes.append(MyNote.getNote(ordinal))

                    for i in range(0, len(keyNoteOrdinals)):
                        keyNoteLookup[thisKey][keyNoteOrdinals[i]] = i

                    for i in range(0, len(keyNoteOrdinals)):
                        startOrdinal = keyNoteOrdinals[i]

                        keyNotes[thisKey][startOrdinal] = {}

                        for j in range(0, len(noteOffsets)):
                            noteOffset = noteOffsets[j]

                            thisIndex = i + noteOffset

                            if thisIndex < 0 or thisIndex >= len(keyNoteOrdinals) - 1:
                                continue

                            keyNotes[thisKey][startOrdinal][noteOffset] = keyNoteOrdinals[thisIndex]

                    break

        return keyNotes, keyNoteLookup

    KEY_NOTES, KEY_NOTE_LOOKUP = setKeyNotes.__func__()

    @staticmethod
    def shiftNote(thisKey, startingNote, positions):
        if thisKey not in MusicHelper.KEY_NOTES:
            print(f"missing {thisKey}")
            return None

        ordinal = MyNote.getNoteOrdinal(startingNote)

        if ordinal not in MusicHelper.KEY_NOTES[thisKey]:
            print(f"missing {startingNote}")
            return None

        if positions not in MusicHelper.KEY_NOTES[thisKey][ordinal]:
            print(f"missing {startingNote}")
            return None

        thisOrdinal = MusicHelper.KEY_NOTES[thisKey][ordinal][positions]

        predictedNote = MyNote.getNote(thisOrdinal)

        return thisOrdinal

    @staticmethod
    def keyNoteDiff(thisKey, noteOne, noteTwo):
        if thisKey not in MusicHelper.KEY_NOTE_LOOKUP:
            print(f"missing {thisKey}")
            return None

        noteOneOrdinal = MyNote.getNoteOrdinal(noteOne)
        noteTwoOrdinal = MyNote.getNoteOrdinal(noteTwo)

        if noteOneOrdinal not in MusicHelper.KEY_NOTE_LOOKUP[thisKey]:
            print(f"missing {noteOneOrdinal}")
            return None

        if noteTwoOrdinal not in MusicHelper.KEY_NOTE_LOOKUP[thisKey]:
            print(f"missing {noteTwoOrdinal}")
            return None

        return MusicHelper.KEY_NOTE_LOOKUP[thisKey][noteTwoOrdinal] - MusicHelper.KEY_NOTE_LOOKUP[thisKey][noteOneOrdinal]
