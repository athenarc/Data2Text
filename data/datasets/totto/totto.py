import json

from torch.utils.data import Dataset


class Totto(Dataset):
    def __init__(self, cfg, type_path, tokenizer):
        if type_path == "train":
            dataset_path = cfg.DATASET.TRAIN
        elif type_path == "validation":
            dataset_path = cfg.DATASET.VALIDATION
        else:
            raise ValueError("Supported type_paths: train, validation")

        with open(dataset_path, encoding="utf-8") as f:
            self.dataset = json.load(f)

        self.input_length = cfg.MODEL.MAX_INPUT_TOKENS
        self.output_length = cfg.MODEL.MAX_OUTPUT_TOKENS
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.dataset)

    # def clean_text(self, text):
    #     text = text.replace('Example of text:', '')
    #     text = text.replace('Example of Summary:', '')
    #     text = text.replace('\n', '')
    #     text = text.replace('``', '')
    #     text = text.replace('"', '')
    #
    #     return text

    def convert_to_features(self, example_batch):
        # Tokenize contexts and questions (as pairs of inputs)
        input_ = example_batch['subtable_and_metadata']
        target_ = example_batch['final_sentence']

        source = self.tokenizer.batch_encode_plus([input_], max_length=self.input_length,
                                                  padding='max_length', truncation=True, return_tensors="pt")

        targets = self.tokenizer.batch_encode_plus([target_], max_length=self.output_length,
                                                   padding='max_length', truncation=True, return_tensors="pt")

        return source, targets

    def __getitem__(self, index):
        source, targets = self.convert_to_features(self.dataset[index])

        source_ids = source["input_ids"].squeeze()
        target_ids = targets["input_ids"].squeeze()

        src_mask = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()

        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}
