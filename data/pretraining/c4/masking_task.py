import json
import math
import random
from itertools import groupby
from operator import itemgetter
from typing import List, Tuple

from nltk.tokenize import word_tokenize
from tqdm import tqdm

from data.pretraining.c4.processing import find_all_files


def find_number_of_masks(tokens_numb: int, rate: float = 0.15) -> int:
    return math.ceil(tokens_numb * rate)


def pick_masked_tokens_inds(total_tokens: int, masks_numb: int) -> List[int]:
    return sorted(random.sample(range(total_tokens), masks_numb))


def apply_mask(tokens: List[str], mask_inds: List[int]) -> Tuple[List[str], List[str]]:
    """
    Look into https://huggingface.co/docs/transformers/model_doc/t5#training
    for more info about how masking works on T5.
    """
    mask_spans = []
    for k, g in groupby(enumerate(mask_inds), lambda ix: ix[0] - ix[1]):
        mask_spans.append(list(map(itemgetter(1), g)))

    target_tokens = []
    for ind, mask_span in enumerate(mask_spans):
        target_tokens.append(f"<extra_id_{ind}>" + " ".join(tokens[mask_span[0]:mask_span[-1]+1]))
    target_tokens.append(f"<extra_id_{len(mask_spans)}>")

    masked_sent = tokens.copy()
    for ind, mask_span in enumerate(mask_spans):
        masked_sent[mask_span[0]] = f'<extra_id_{ind}>'
        for mask_tail in mask_span[1:]:
            masked_sent[mask_tail] = '<<REMOVE>>'

    masked_sent = [token for token in masked_sent if token != '<<REMOVE>>']

    return masked_sent, target_tokens


def perform_span_masking(sentence: str, mask_rate: float = 0.15) -> Tuple[str, str]:
    tokens = word_tokenize(sentence)

    mask_inds = pick_masked_tokens_inds(len(tokens),
                                        find_number_of_masks(len(tokens), rate=mask_rate))

    masked_sent, masked_tokens = apply_mask(tokens, mask_inds)

    return " ".join(masked_sent), "".join(masked_tokens)


def c4_masking_task(disable_tqdm=True):
    C4_PROCESSED_DIR = "storage/datasets/c4/processed/"
    C4_MASKED_DIR = "storage/datasets/c4/masked/"

    # Get all the c4 parts that we will use
    file_paths = find_all_files(C4_PROCESSED_DIR)

    for ind, file_path in enumerate(file_paths):
        print(f"C4 | Span masking | File: {ind + 1} / {len(file_paths)}")

        # Reading
        with open(file_path, 'r') as inp:
            processed_c4 = json.load(inp)

        # Span masking
        masked_c4 = []
        for sent in tqdm(processed_c4, disable=disable_tqdm):
            masked_sent, target_tokens = perform_span_masking(sent, mask_rate=0.15)
            masked_c4.append({
                "totto_original": sent,
                "totto_task": masked_sent,
                "target": target_tokens
            })

        # Store
        with open(C4_MASKED_DIR + file_path.split('/')[-1], 'w') as outfile:
            json.dump(masked_c4, outfile)

    print("DONE!")


if __name__ == '__main__':
    c4_masking_task(disable_tqdm=False)
