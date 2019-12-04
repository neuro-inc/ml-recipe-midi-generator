import logging
from collections import defaultdict

import torch
import torch.nn as nn
from .loss import LabelSmoothingLossWithLogits
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, RandomSampler
from tqdm import tqdm

logger = logging.getLogger(__file__)


class AverageMeter:
    def __init__(self):
        self._counter = 0
        self._avg_value = 0

    def __call__(self):
        return self._avg_value

    def update(self, value):
        self._counter += 1
        self._avg_value = (self._avg_value * (self._counter - 1) + value) / self._counter


class Trainer:
    def __init__(self,
                 model,
                 vocab, train_dataset, writer, *, device=torch.device('cuda'),
                 train_batch_size=32, batch_split=1, n_jobs=4, n_epochs=0, lr=1e-3,
                 weight_decay=5e-4, w_cls=1, w_off=10, smoothing=0) -> None:

        logger.info(f'Used device: {device}.')

        self.vocab = vocab
        self.model = model.to(device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr, weight_decay=weight_decay)

        self.cls_criteria = LabelSmoothingLossWithLogits(n_classes=len(vocab), smoothing=smoothing,
                                                         ignore_index=vocab.pad_index).to(device)
        self.off_criteria = nn.SmoothL1Loss().to(device)

        logger.info(f'Train Dataset len: {len(train_dataset)}.')

        train_sampler = RandomSampler(train_dataset)
        self.train_dataloader = torch.utils.data.DataLoader(train_dataset,
                                                            batch_size=int(train_batch_size // batch_split),
                                                            num_workers=n_jobs,
                                                            sampler=train_sampler,
                                                            drop_last=True,
                                                            collate_fn=self.collate_fun)

        self.device = device
        self.batch_split = batch_split
        self.n_epochs = n_epochs
        self.writer = writer
        self.global_step = 0

        self.w_cls = w_cls
        self.w_off = w_off

    def collate_fun(self, data):
        prevs = [torch.LongTensor(d[0]) for d in data]
        nexts = [torch.LongTensor(d[1]) for d in data]
        prev_offsets = [torch.FloatTensor(d[2]) for d in data]
        next_offsets = [torch.FloatTensor(d[3]) for d in data]

        prevs = pad_sequence(prevs, batch_first=True, padding_value=self.vocab.pad_index).to(self.device)
        nexts = pad_sequence(nexts, batch_first=True, padding_value=self.vocab.pad_index).to(self.device)

        prev_offsets = pad_sequence(prev_offsets, batch_first=True, padding_value=0).to(self.device)
        next_offsets = pad_sequence(next_offsets, batch_first=True, padding_value=0).to(self.device)

        return prevs, nexts, prev_offsets, next_offsets

    def train(self):
        for epoch_i in range(1, self.n_epochs+1):
            self._train(epoch_i)

    def _train(self, epoch_i):
        self.model.train()
        self.optimizer.zero_grad()

        avg_losses = defaultdict(AverageMeter)

        tqdm_data = tqdm(self.train_dataloader, desc=f'Train (epoch #{epoch_i} / {self.n_epochs})')

        for i, batch in enumerate(tqdm_data):
            prevs, nexts, prev_offsets, next_offsets = batch
            model_nexts, model_offsets, _ = self.model(prevs, prev_offsets)

            class_loss = self.cls_criteria(model_nexts.view(-1, model_nexts.size(-1)),
                                           nexts.view(-1))

            content_mask = torch.ne(prevs, self.vocab.pad_index)
            offset_loss = self.off_criteria(content_mask.float() * model_offsets.squeeze(-1), next_offsets)

            loss = self.w_cls * class_loss + self.w_off * offset_loss

            avg_losses['class_loss'].update(class_loss.item())
            avg_losses['offset_loss'].update(offset_loss.item())
            avg_losses['loss'].update(loss.item())

            loss = loss / self.batch_split
            loss.backward()

            if (i + 1) % self.batch_split == 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 10.0)
                self.optimizer.step()
                self.optimizer.zero_grad()

                for k, v in avg_losses.items():
                    self.writer.add_scalar(f'training/{k}', v(), global_step=self.global_step)

                self.global_step += 1

            tqdm_data.set_postfix({k: v() for k, v in avg_losses.items()})

    def save_state_dict(self, path_):
        model_dict = self.model.state_dict()
        unique_notes = self.vocab.unique_notes

        state_dict = {'model': model_dict,
                      'unique_notes': unique_notes,
                      'model_repr': repr(self.model),
                      'global_step': self.global_step}

        torch.save(state_dict, path_)

        logger.info(f'State dict was saved to {path_}.')
