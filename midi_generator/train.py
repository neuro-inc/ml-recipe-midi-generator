import logging
import os
from pathlib import Path

import configargparse
import torch
from torch.utils.tensorboard import SummaryWriter

from model.dataset import MidiDataset
from model.model import GRUNet
from model.trainer import Trainer
from utils.seed import set_seed


def get_parser() -> configargparse.ArgumentParser:
    parser = configargparse.ArgumentParser(description='Midi-generator training script.')

    parser.add_argument('-c', '--config_file', required=False, is_config_file=True, help='Config file path.')

    parser.add_argument('--dump_dir', type=Path, default='../results', help='Dump path.')
    parser.add_argument('--experiment_name', type=str, required=True, help='Experiment name.')

    parser.add_argument('--m_hidden_dim', type=int, default=256, help='Model hidden size.')
    parser.add_argument('--m_n_layers', type=int, default=2, help='Number GRU layers.')
    parser.add_argument('--m_drop_prob', type=float, default=.2, help='Dropout proba.')

    parser.add_argument('--gpu', action='store_true', help='Use gpu to train model.')

    parser.add_argument('--seed', type=int, default=0, help='Seed for random state.')

    parser.add_argument('--n_jobs', type=int, default=2, help='Number of threads in data loader.')
    parser.add_argument('--n_epochs', type=int, default=10, help='Number of epochs.')

    parser.add_argument('--batch_size', type=int, default=128, help='Number of items in batch.')
    parser.add_argument('--batch_split', type=int, default=1,
                        help='Batch will be split into this number chunks during training.')

    parser.add_argument('--lr', type=float, default=6.25e-5, help='Learning rate for optimizer.')
    parser.add_argument('--weight_decay', type=float, default=0.01, help='Weight decay for optimizer.')
    parser.add_argument('--smoothing', type=float, default=0, help='Smooth coefficient.')

    parser.add_argument('--w_cls', type=float, default=1, help='Class criteria weight.')
    parser.add_argument('--w_off', type=float, default=10., help='Offset criteria weight.')

    parser.add_argument('--data_prefix', type=str, required=True, help='Prefix of train *.mid files.')
    parser.add_argument('--data_coef', type=int, default=100,
                        help='Expand dataset coefficient. The number of real elements will be multiplied by this '
                             'coefficient to expand length of the dataset.')
    parser.add_argument('--data_seq_len', type=int, default=256,
                        help='Lenght of sequences which are used to train the model.')

    return parser


def show_params(params: configargparse.Namespace) -> None:
    logger.info('Input parameters:')
    for k in sorted(params.__dict__.keys()):
        logger.info(f'\t{k}: {getattr(params, k)}')


def main() -> None:
    params = get_parser().parse_args()
    show_params(params)
    os.makedirs(params.dump_dir, exist_ok=True)

    set_seed(params.seed)

    device = torch.device('cuda') if torch.cuda.is_available() and params.gpu else torch.device('cpu')

    dataset = MidiDataset(data_prefix=params.data_prefix, seq_len=params.data_seq_len, expand_coef=params.data_coef)
    vocab = dataset.vocab

    model = GRUNet(num_embeddings=len(vocab),
                   hidden_dim=params.m_hidden_dim,
                   n_layers=params.m_n_layers,
                   drop_prob=params.m_drop_prob)

    writer = SummaryWriter(log_dir=params.dump_dir / f'board/{params.experiment_name}')

    trainer = Trainer(model, vocab, dataset,
                      writer=writer,
                      device=device,
                      train_batch_size=params.batch_size,
                      batch_split=params.batch_split,
                      n_jobs=params.n_jobs,
                      n_epochs=params.n_epochs,
                      lr=params.lr,
                      weight_decay=params.weight_decay,
                      w_cls=params.w_cls,
                      w_off=params.w_off,
                      smoothing=params.smoothing)

    trainer.train()
    trainer.save_state_dict(params.dump_dir / f'{params.experiment_name}.ch')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    logger = logging.getLogger(__file__)

    main()
