import logging

import configargparse
import torch
from music21 import stream

from model.dataset import MidiDataset, Vocab
from utils.generate_midi import generate_midi
from utils.load_model import load_model
from utils.seed import set_seed


def get_parser() -> configargparse.ArgumentParser:
    def cast2(type_):
        return lambda x: type_(x) if x != 'None' else None

    parser = configargparse.ArgumentParser(description='Midi-generator.')

    parser.add_argument('-c', '--config_file', required=False, is_config_file=True, help='Config file path.')

    parser.add_argument('--checkpoint_path', type=str, required=True, help='Model checkpoint path.')

    parser.add_argument('--seq_len', type=int, default=256, help='Output sequence length.')
    parser.add_argument('--top_p', type=float, default=0.6, help='Nucleus sampling probability.')
    parser.add_argument('--temperature', type=float, default=1.0, help='Sampling temperature.')

    parser.add_argument('--gpu', action='store_true', help='Use gpu to train model.')
    parser.add_argument('--seed', type=cast2(int), default=None, help='Seed for random state.')

    parser.add_argument('--out', required=True, type=str, help='Out midi file path.')

    return parser


def write_midi(out_file, notes):
    midi_stream = stream.Stream(notes)
    midi_stream.write('midi', fp=out_file)


def main():
    params = get_parser().parse_args()
    if params.seed is not None:
        set_seed(params.seed)

    device = torch.device('cuda') if torch.cuda.is_available() and params.gpu else torch.device('cpu')
    logger.info(f'Used device: {device}')

    model, vocab = load_model(params.checkpoint_path, device=device)

    note_seq, offset_seq = generate_midi(model, vocab,
                                         seq_len=params.seq_len,
                                         top_p=params.top_p,
                                         temperature=params.temperature)
    note_seq = vocab.decode(note_seq)
    notes = MidiDataset.decode_notes(note_seq, offset_seq)

    write_midi(params.out, notes)

    logger.info(f'Result was saved to {params.out}.')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    logger = logging.getLogger(__file__)

    main()
