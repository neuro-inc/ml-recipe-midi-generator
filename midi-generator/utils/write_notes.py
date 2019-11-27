from music21 import stream


def write_notes(out_file, notes):
    midi_stream = stream.Stream(notes)
    midi_stream.write('midi', fp=out_file)
