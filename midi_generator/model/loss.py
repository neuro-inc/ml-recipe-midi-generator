import torch
import torch.nn as nn


class LabelSmoothingLossWithLogits(nn.Module):
    def __init__(self, n_classes, *, smoothing=0.0, ignore_index=-100):
        super().__init__()

        assert 0 <= smoothing <= 1

        self.ignore_index = ignore_index
        self.n_classes = n_classes

        self.smoothing = smoothing
        self.confidence = 1 - smoothing

        self.num_ignore_ixs = 1 + (0 <= self.ignore_index < self.n_classes)

        self.criterion = nn.KLDivLoss(reduction='batchmean') if smoothing > 0 else nn.NLLLoss(ignore_index=ignore_index)

    def forward(self, input_logits, targets):

        log_probas = torch.log_softmax(input_logits, dim=-1)

        if self.smoothing > 0:
            batch_size = targets.size(0)
            fill_value = self.smoothing / (self.n_classes - self.num_ignore_ixs)

            with torch.no_grad():
                target_dist = torch.full((batch_size, self.n_classes), fill_value=fill_value,
                                         device=targets.device)
                target_dist.scatter_(-1, targets.unsqueeze(-1), self.confidence)
                if 0 <= self.ignore_index < self.n_classes:
                    target_dist[:, self.ignore_index] = 0

            targets = target_dist

        return self.criterion(log_probas, targets)
