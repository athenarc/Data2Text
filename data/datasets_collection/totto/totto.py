import glob
import json

from torch.utils.data import Dataset
from transformers import BatchEncoding, T5Tokenizer  # Typing

from tools.enums import Mode


class Totto(Dataset):
    def __init__(self, cfg, type_path, tokenizer):
        if type_path == Mode.TRAIN:
            dataset_path = cfg.DATASET.TRAIN
        elif type_path == Mode.VALIDATION:
            dataset_path = cfg.DATASET.VALIDATION
        else:
            raise ValueError("Supported type_paths: train, validation")

        self.mode = type_path
        if dataset_path[-1] != '/':
            # Case that the dataset is a single file
            with open(dataset_path, encoding="utf-8") as f:
                self.dataset = json.load(f)
        else:
            # Case that the dataset is a directory of files
            self.dataset = []
            dataset_paths = glob.glob(dataset_path + "/*")
            for path in dataset_paths:
                with open(path, encoding="utf-8") as f:
                    single_dataset = json.load(f)
                self.dataset.extend(single_dataset)

        self.input_length: int = cfg.MODEL.MAX_INPUT_TOKENS
        self.output_length: int = cfg.MODEL.MAX_OUTPUT_TOKENS
        self.tokenizer: T5Tokenizer = tokenizer

    def __len__(self) -> int:
        return len(self.dataset)

    def convert_to_features(self, example_batch):
        """ Transform the input strings into token ids using the T5 tokenizer """

        # Tokenize contexts and questions (as pairs of inputs)
        input_ = example_batch['subtable_and_metadata']
        target_ = example_batch['final_sentence']

        source = self.tokenizer.batch_encode_plus([input_], max_length=self.input_length,
                                                  padding='max_length', truncation=True,
                                                  add_special_tokens=True, return_tensors="pt")

        targets = self.tokenizer.batch_encode_plus([target_], max_length=self.output_length,
                                                   padding='max_length', truncation=True,
                                                   add_special_tokens=True, return_tensors="pt")

        return source, targets

    @staticmethod
    def get_ids(source, targets):
        source_ids = source["input_ids"].squeeze()
        target_ids = targets["input_ids"].squeeze()

        src_mask = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()

        return {"source_ids": source_ids, "source_mask": src_mask,
                "target_ids": target_ids, "target_mask": target_mask}

    # @staticmethod
    # def get_val_ids(source, targets):
    #     source_ids = source["input_ids"].squeeze()
    #     list_target_ids = targets["input_ids"].squeeze()
    #
    #     src_mask = source["attention_mask"].squeeze()
    #     target_mask = targets["attention_mask"].squeeze()
    #
    #     return {"source_ids": source_ids, "source_mask": src_mask,
    #             "target_ids": target_ids, "target_mask": target_mask}

    def __getitem__(self, index):
        source, targets = self.convert_to_features(self.dataset[index])

        # if self.mode is Mode.TRAIN:
        return self.get_ids(source, targets)
