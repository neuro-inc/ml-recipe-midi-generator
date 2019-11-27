import random
import torch
from tqdm.auto import tqdm


def generate_midi(model, vocab, *, seq_len=1024, top_p=0.6, temperature=1.0):
    assert 0 <= top_p <= 1
    assert 0 < temperature

    model.eval()

    predicted_seq = [random.randint(0, len(vocab) - 1)]
    offsets = [0]

    h = None

    with torch.no_grad():
        for _ in tqdm(range(seq_len)):
            inputs = torch.LongTensor(predicted_seq[-1:]).unsqueeze(0)
            input_offsets = torch.FloatTensor(offsets[-1:]).unsqueeze(0)

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
