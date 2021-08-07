from typing import List  # Typing

from transformers import T5Tokenizer  # Typing


def ids_to_clean_text(tokenizer: T5Tokenizer, generated_ids: List[List[int]]) -> List[str]:
    gen_text = tokenizer.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    )
    return list(map(str.strip, gen_text))
