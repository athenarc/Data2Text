import json

import torch
from tqdm import tqdm
from transformers import T5Tokenizer
from wandb.wandb_run import Run  # Typing
from yacs.config import CfgNode  # Typing

from modeling.T5Module import T5System
from utils.model import add_batch_dim
from visualizing.wandb_inference_report import create_inference_report_on_wandb


class InferenceController:
    """
    The controller in its current state does not support batch inference.
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


def get_eval_model_and_tokenizer(cfg: CfgNode, device):
    # Get the T5 tokenizer
    tokenizer = T5Tokenizer.from_pretrained(cfg.MODEL.TOKENIZER_NAME)

    # Load the model
    model = T5System.load_from_checkpoint(cfg.MODEL.PATH_TO_CHECKPOINT,
                                          cfg=cfg, tokenizer=tokenizer)
    model.to(device)
    model.eval()

    return tokenizer, model


def evaluate(cfg: CfgNode, wandb_run: Run) -> None:
    inference_controller = InferenceController(cfg)
    with open(cfg.DATASET.EVALUATION) as f:
        eval_set = json.load(f)

    inferences = [inference_controller.inference(datapoint['subtable_and_metadata'])
                  for datapoint in tqdm(eval_set)]

    targets = [datapoint['final_sentence'] for datapoint in eval_set]
    if type(targets[0]) is str:
        # Maybe our evaluation set contains single references
        # In this case we are adding the list dimension
        targets = [[target] for target in targets]

    sources = [datapoint['subtable_and_metadata'] for datapoint in eval_set]

    create_inference_report_on_wandb(wandb_run, inferences, targets, sources,
                                     inference_controller.tokenizer)
