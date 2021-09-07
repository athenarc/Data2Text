import logging

import torch
from transformers import T5Tokenizer
from yacs.config import CfgNode  # Typing

from modeling.T5Module import T5System
from utils.model import add_batch_dim


class InferenceController:
    """"
    This module and the backend package in general is coupled with the rest of the repo.
    Eg. from modeling.T5Module import T5System
    In the future the app code and the model development code should have the least possible
    coupling.
    """
    def __init__(self, cfg: CfgNode):
        self.cfg = cfg
        self.tokenizer, self.model, self.device = self.load_tokenizer_and_model()

    def load_tokenizer_and_model(self):
        # Get the T5 tokenizer
        tokenizer = T5Tokenizer.from_pretrained(self.cfg.MODEL.TOKENIZER_NAME)

        # Load the model
        model = T5System.load_from_checkpoint(self.cfg.MODEL.PATH_TO_CHECKPOINT,
                                              cfg=self.cfg, tokenizer=tokenizer)

        device = self.get_device()

        model.to(device)
        model.eval()

        return tokenizer, model, device

    def get_device(self):
        if self.cfg.MODEL.DEVICE == "cuda":
            if torch.cuda.is_available():
                return torch.device("cuda:0")
            else:
                logging.warning("Requested cuda enabled device but none found.")
                return torch.device("cpu")
        else:
            return torch.device("cpu")

    def tokenize(self, table_info: str):
        """ table_info is the linearized table """
        source = self.tokenizer.batch_encode_plus([table_info], max_length=self.cfg.MODEL.MAX_INPUT_TOKENS,
                                                  padding='max_length', truncation=True,
                                                  add_special_tokens=True, return_tensors="pt")

        return {"source_ids": source["input_ids"].squeeze(),
                "source_mask": source["attention_mask"].squeeze()}

    def inference(self, table_info):
        datapoint = self.tokenize(table_info)
        datapoint = add_batch_dim([datapoint], self.device)[0]

        table_verbalization = self.model.inference_without_target(datapoint)

        return table_verbalization[0]
