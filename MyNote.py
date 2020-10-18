import music21


class MyNote:
    note = None
    noteOrdinal = None

    @staticmethod
    def getNoteOrdinals():
        noteOrdinals = {}
        noteOrdinals["A0"] = 1
        noteOrdinals["B-0"] = 2
        noteOrdinals["B0"] = 3

        noteOrdinal = 4
        for octave in range(1, 8):
            for note_list in [
                ["C"],
                ["C#", "D-"],
                ["D"],
                ["D#", "E-"],
                ["E"],
                ["F"],
                ["F#", "G-"],
                ["G"],
                ["G#", "A-"],
                ["A"],
                ["A#", "B-"],
                ["B"],
            ]:
                for note in note_list:
                    noteOrdinals[f"{note}{octave}"] = noteOrdinal
                noteOrdinal = noteOrdinal + 1

        noteOrdinals["C"] = noteOrdinal

        return noteOrdinals

    NOTE_ORDINALS = getNoteOrdinals.__func__()

    @staticmethod
    def getNoteOrdinal(note):
        if note.nameWithOctave in MyNote.NOTE_ORDINALS:
            return MyNote.NOTE_ORDINALS[note.nameWithOctave]
        else:
            print("nope -> " + note.nameWithOctave)

    def __init__(self, note):
        self.note = note
        self.noteOrdinal = MyNote.getNoteOrdinal(note)
