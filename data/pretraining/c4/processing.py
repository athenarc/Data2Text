import glob
import json
import random
from typing import List

from sentence_splitter import split_text_into_sentences
from tqdm import tqdm


def preprocess(texts: List[str]) -> List[str]:
    """
    * Remove newlines
    * Sentence splitting
    * Shuffling
    """
    c4 = [text.replace('\n', ' ') for text in texts]

    # Sentence split
    c4_sentences = []
    for text in tqdm(c4):
        sents = split_text_into_sentences(text, language='en')
        c4_sentences.extend(sents)

    random.shuffle(c4_sentences)

    return c4_sentences


def find_all_files(c4_dir: str) -> List[str]:
    return [path for path in glob.glob(f"{c4_dir}*")]


if __name__ == '__main__':
    C4_ORIGINAL_DIR = "storage/datasets/c4/original/"
    C4_OUTPUT_DIR = "storage/datasets/c4/processed/"

    # Get all the c4 parts that we will use
    file_paths = find_all_files(C4_ORIGINAL_DIR)

    for ind, file_path in enumerate(file_paths):
        print(f"File: {ind} / {len(file_paths)}")

        # Reading
        with open(file_path) as f:
            c4_original = [json.loads(line)['text'] for line in f]

        # Processing
        c4_processed = preprocess(c4_original)

        # Store
        with open(C4_OUTPUT_DIR + file_path.split('/')[-1], 'w') as outfile:
            json.dump(c4_processed, outfile)

    print("DONE!")
