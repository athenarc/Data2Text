# from typing import List  # Typing

import torch
from transformers import T5Tokenizer  # Typing


def ids_to_clean_text(tokenizer, generated_ids):
    gen_text = tokenizer.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )
    return list(map(str.strip, gen_text))


def add_batch_dim(list_of_dicts, device):
    """
    Add a dummy batch axis in front of the tensors in the dict.
    Also, send the tensors to the device (gpu or cpu).
    """
    ret_list = []
    for diction in list_of_dicts:
        ret_list.append({key: value.unsqueeze_(0).to(device)
                         for key, value in diction.items()})

    return ret_list
