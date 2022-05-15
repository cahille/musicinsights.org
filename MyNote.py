import music21


class MyNote:
    note = None
    noteOrdinal = None

    @staticmethod
    def getNotesByOrdinals(noteOrdinals):
        notesByOrdinals = {}

        for note, ordinal in noteOrdinals.items():
            notesByOrdinals[ordinal] = note

        return notesByOrdinals

    @staticmethod
    def getNoteOrdinals():
        noteOrdinals = {}
        noteOrdinals["A0"] = 1
        noteOrdinals["B-0"] = 2
        noteOrdinals["B0"] = 3

        noteOrdinal = 4
        for octave in range(1, 8):
            for note_list in [
                ["C", "B#"],
                ["C#", "D-"],
                ["D", "C##", "E--"],
                ["D#", "E-"],
                ["E", "F-"],
                ["F", "E#"],
                ["F#", "G-"],
                ["G", "F##"],
                ["G#", "A-"],
                ["A", "B--"],
                ["A#", "B-"],
                ["B", "C-"],
            ]:
                for note in note_list:
                    noteOrdinals[f"{note}{octave}"] = noteOrdinal
                noteOrdinal = noteOrdinal + 1

        noteOrdinals["C"] = noteOrdinal

        return noteOrdinals

    NOTE_ORDINALS = getNoteOrdinals.__func__()
    NOTES_BY_ORDINALS = getNotesByOrdinals.__func__(NOTE_ORDINALS)

    @staticmethod
    def getNoteOrdinal(note):
        if note.nameWithOctave in MyNote.NOTE_ORDINALS:
            return MyNote.NOTE_ORDINALS[note.nameWithOctave]
        else:
            print("nope -> " + note.nameWithOctave)

    @staticmethod
    def getNoteWithOctave(ordinal):
        if int(ordinal) in MyNote.NOTES_BY_ORDINALS:
            return MyNote.NOTES_BY_ORDINALS[int(ordinal)] \
                .replace('B--', 'A') \
                .replace('B#', 'C') \
                .replace('C-', 'B') \
                .replace('E--', 'D') \
                .replace('E#', 'F') \
                .replace('F-', 'E') \
                .replace('F##', 'G')
        else:
            print("nope -> " + ordinal)

    @staticmethod
    def getNote(ordinal):
        return MyNote.getNoteWithOctave(ordinal).replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8',
                                                                                                                                                                                '')

    def __init__(self, note):
        self.note = note
        self.noteOrdinal = MyNote.getNoteOrdinal(note)
