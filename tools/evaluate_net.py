import random

import numpy as np
from enums import Mode
from transformers import T5Tokenizer
from wandb.wandb_run import Run  # Typing
from yacs.config import CfgNode  # Typing

from data.datasets.totto.totto import Totto
from data.datasets.totto.utils import retrieve_table_source
from modeling.T5Module import T5System
from utils.model import list_dict_values
from visualizing.wandb_table import create_inference_examples_table


def evaluate(cfg: CfgNode, wandb_run: Run) -> None:
    # Get the T5 tokenizer
    tokenizer = T5Tokenizer.from_pretrained(cfg.MODEL.TOKENIZER_NAME)

    # Load the model
    model = T5System.load_from_checkpoint(cfg.MODEL.PATH_TO_CHECKPOINT,
                                          cfg=cfg, tokenizer=tokenizer)
    model.eval()

    # Get the validation dataset
    validation_dataset = list(Totto(cfg, Mode.VALIDATION, tokenizer))

    # We need the indexes in order to retrieve the source input without having to decode
    validation_sample_inds = random.sample(list(np.arange(len(validation_dataset))), 50)

    # Prepare both the table sources
    table_sources = retrieve_table_source(cfg.DATASET.VALIDATION, validation_sample_inds)
    datapoints = [validation_dataset[ind] for ind in validation_sample_inds]
    datapoints = list_dict_values(datapoints)

    inferences_targets = [model.inference(datapoint) for datapoint in datapoints]
    inferences_targets = [[inf[0], target[0]] for inf, target in inferences_targets]

    create_inference_examples_table(wandb_run, inferences_targets, table_sources)
