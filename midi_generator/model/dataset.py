import copy
import glob
import logging
import os
import random
from itertools import cycle

from music21 import converter, instrument, note, chord
from tqdm import tqdm

logger = logging.getLogger(__file__)


class Vocab(object):
    _pad_token = '<PAD>'
    _pad_index = 0

    def __init__(self, unique_notes):
        self.unique_notes = copy.deepcopy(unique_notes)

        self.note2id = {n: i for i, n in enumerate(self.unique_notes, start=1)}
        self.note2id[self._pad_token] = self._pad_index

        self.id2note = {i: n for n, i in self.note2id.items()}

    def __len__(self):
        return len(self.note2id)

    @property
    def pad_index(self):
        return self._pad_index

    def encode(self, notes):
        return [self.note2id[c] for c in notes]

    def decode(self, idxs):
        return [self.id2note[i] for i in idxs]


class MidiDataset(object):
    def __init__(self, *, data_prefix, seq_len, expand_coef):
        self.data_prefix = data_prefix
        self.seq_len = seq_len

        self.__load_files()

        self.vocab = Vocab(list(sorted(set(sum(self.note_seqs, [])))))
        self.note_seqs = [self.vocab.encode(seq) for seq in self.note_seqs]

        self.expand_coef = expand_coef

    @staticmethod
    def encode_notes(notes):
        note_seq = []
        offset_seq = []

        prev_time = 0

        for element in notes:
            if isinstance(element, note.Note):
                note_seq.append(str(element.pitch))
                offset_seq.append(float(element.offset) - prev_time)
                prev_time = element.offset
            elif isinstance(element, chord.Chord):
                note_seq.append('.'.join(str(n) for n in element.normalOrder))
                offset_seq.append(float(element.offset) - prev_time)
                prev_time = element.offset

        return note_seq, offset_seq

    @staticmethod
    def decode_notes(note_seq, offset_seq=None):
        total_offset = 0
        notes = []

        offset_seq = cycle([0.5]) if offset_seq is None else offset_seq

        for pattern, offset in zip(note_seq, offset_seq):
            total_offset += min(max(offset, 0), 1)

            if ('.' in pattern) or pattern.isdigit():
                notes_in_chord = pattern.split('.')
                chord_notes = []
                for current_note in notes_in_chord:
                    new_note = note.Note(int(current_note))
                    new_note.storedInstrument = instrument.Piano()
                    chord_notes.append(new_note)

                new_chord = chord.Chord(chord_notes)
                new_chord.offset = total_offset
                notes.append(new_chord)
            else:
                new_note = note.Note(pattern)
                new_note.offset = total_offset
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)

        return notes

    @staticmethod
    def load_raw_notes(file_path):
        midi = converter.parse(file_path)
        parts = instrument.partitionByInstrument(midi)
        raw_notes = parts.parts[0].recurse() if instrument.partitionByInstrument(midi) else midi.flat.notes

        return raw_notes

    def __load_files(self):
        self.note_seqs = []
        self.offset_seqs = []

        files = tqdm(glob.glob(self.data_prefix + '*.mid'), desc=f'Loading files with prefix [{self.data_prefix}]')
        for file in files:
            raw_notes = MidiDataset.load_raw_notes(file)
            note_seq, offset_seq = MidiDataset.encode_notes(raw_notes)

            self.note_seqs.append(note_seq)
            self.offset_seqs.append(offset_seq)

    def __len__(self):
        return self.expand_coef * len(self.note_seqs)

    def __getitem__(self, idx):
        idx = idx % len(self.note_seqs)

        seq = self.note_seqs[idx]
        offsets = self.offset_seqs[idx]

        if len(seq) < 3:
            # logger.info('Too short file was replaced with another one.')
            return self.__getitem__(random.randint(0, len(self) - 1))

        start_idx = random.randint(0, len(seq) - 2)

        prevs = seq[start_idx:start_idx + self.seq_len]
        nexts = seq[start_idx + 1:start_idx + self.seq_len + 1]

        prev_offsets = offsets[start_idx:start_idx + self.seq_len]
        next_offsets = offsets[start_idx + 1:start_idx + self.seq_len + 1]

        if len(prevs) > len(nexts):
            prevs = prevs[:-1]
            prev_offsets = prev_offsets[:-1]

        # to make sure that the first note has zero offset
        prev_offsets[0] = 0

        assert len(prevs) == len(nexts)

        return prevs, nexts, prev_offsets, next_offsets
