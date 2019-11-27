import torch

from model.dataset import Vocab
from model.model import GRUNet


def load_model(checkpoint_path, device=torch.device('cpu')):
    state_dict = torch.load(checkpoint_path)

    model = eval(state_dict['model_repr'])
    model.load_state_dict(state_dict['model'])

    vocab = Vocab(state_dict['unique_notes'])

    model.to(device)
    model.eval()

    return model, vocab
