import random

import numpy as np
import torch
from transformers import T5Tokenizer
from wandb.wandb_run import Run  # Typing
from yacs.config import CfgNode  # Typing

from data.datasets_collection.totto.totto import Totto
from data.datasets_collection.totto.utils import retrieve_table_source
from modeling.T5Module import T5System
from tools.enums import Mode
from utils.model import add_batch_dim
from visualizing.wandb_table import create_inference_examples_table


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
    # Get the inference device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    tokenizer, model = get_eval_model_and_tokenizer(cfg, device)

    # Get the validation dataset
    validation_dataset = list(Totto(cfg, Mode.VALIDATION, tokenizer))

    # We need the indexes in order to retrieve the source input without having to decode
    validation_sample_inds = random.sample(list(np.arange(len(validation_dataset))), 50)

    # Prepare both the table sources
    table_sources = retrieve_table_source(cfg.DATASET.VALIDATION, validation_sample_inds)
    datapoints = [validation_dataset[ind] for ind in validation_sample_inds]
    datapoints = add_batch_dim(datapoints, device)  # The inference method expects a batch of datapoints

    inferences_targets = [model.inference(datapoint) for datapoint in datapoints]
    inferences_targets = [[inf[0], target[0]] for inf, target in inferences_targets]

    create_inference_examples_table(wandb_run, inferences_targets, table_sources, tokenizer)
