import random
import torch
from tqdm.auto import tqdm


@torch.no_grad()
def generate_midi(model, vocab, *, seq_len=1024, top_p=0.6, temperature=1.0, device=torch.device('cpu'),
                  history=None):
    """
    :param history: [(note_id, offset), ....]
    """
    assert 0 <= top_p <= 1
    assert 0 < temperature

    model.eval()

    if history is None:
        predicted_seq = [random.randint(0, len(vocab) - 1)]
        offsets = [0]
        h = None
    else:
        predicted_seq = [h[0] for h in history]
        offsets = [h[0] for h in history]

        inputs = torch.LongTensor(predicted_seq[:-1]).unsqueeze(0).to(device)
        input_offsets = torch.FloatTensor(offsets[:-1]).unsqueeze(0).to(device)

        _, _, h = model(inputs, input_offsets)

    with torch.no_grad():
        tqdm_data = tqdm(range(seq_len), desc=f'Sound generation')
        for _ in tqdm_data:
            inputs = torch.LongTensor(predicted_seq[-1:]).unsqueeze(0).to(device)
            input_offsets = torch.FloatTensor(offsets[-1:]).unsqueeze(0).to(device)

            output_logits, output_offsets, h = model(inputs, input_offsets, h)
            output_logits = output_logits / temperature

            output_probas = torch.softmax(output_logits, -1)

            sorted_probas, sorted_indexes = torch.sort(output_probas, dim=-1, descending=True)
            cumulative_probas = torch.cumsum(sorted_probas, dim=-1)

            mask_to_remove = cumulative_probas > top_p
            mask_to_remove[:, :, 0] = 0

            sorted_probas.masked_fill_(mask_to_remove, 0)
            output_probas.scatter_(-1, sorted_indexes, sorted_probas)

            next_ids = torch.multinomial(output_probas[0], num_samples=1).item()
            predicted_seq.append(next_ids)
            offsets.append(output_offsets.item())

    return predicted_seq, offsets
