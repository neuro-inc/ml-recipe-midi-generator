import torch
import torch.nn as nn


class GRUNet(nn.Module):
    def __init__(self, *, num_embeddings, hidden_dim, n_layers, drop_prob=0):
        super().__init__()

        self.num_embeddings = num_embeddings
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.drop_prob = drop_prob

        self.off = nn.Linear(1, hidden_dim)
        self.emb = nn.Embedding(num_embeddings, hidden_dim)

        self.norm = nn.LayerNorm(hidden_dim)

        self.gru = nn.GRU(hidden_dim, hidden_dim, n_layers, batch_first=True, dropout=drop_prob)

        self.extract = nn.Sequential(
            nn.ReLU(),
            nn.LayerNorm(hidden_dim))

        self.fc_class = nn.Linear(hidden_dim, num_embeddings, bias=False)
        self.fc_offset = nn.Sequential(nn.Linear(hidden_dim, 1, bias=False),
                                       nn.ReLU())

    def forward(self, x, offsets, h=None):
        if h is None:
            h = self.init_hidden(x.size(0), x.device)
        embedded_x = self.norm(self.emb(x) + self.off(offsets.unsqueeze(-1)))

        rnn_out, h = self.gru(embedded_x, h)

        features = self.extract(rnn_out)

        class_out = self.fc_class(features)
        offset_out = self.fc_offset(features)

        return class_out, offset_out, h

    def init_hidden(self, batch_size, device):
        hidden = torch.zeros((self.n_layers, batch_size, self.hidden_dim),
                             dtype=torch.float, device=device, requires_grad=True)
        return hidden

    def __repr__(self):
        return f'{self.__class__.__name__}(num_embeddings={self.num_embeddings}, hidden_dim={self.hidden_dim}, ' \
               f'n_layers={self.n_layers}, drop_prob={self.drop_prob})'
