import torch
import random
import numpy as np
import logging

logger = logging.getLogger(__file__)


def set_seed(seed: int = 0) -> None:
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True
    torch.manual_seed(seed)

    random.seed(seed)
    np.random.seed(seed)

    logger.info(f'Random seed was set to {seed}.')
