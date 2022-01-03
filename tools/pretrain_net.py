from transformers import T5Tokenizer
from yacs.config import CfgNode  # Typing

from data.build import get_train_dataloader
from engine.pretrain import start_pretrainer


def pretrain(cfg: CfgNode) -> None:
    # Get the T5 tokenizer
    tokenizer = T5Tokenizer.from_pretrained(cfg.MODEL.TOKENIZER_NAME)

    # Get train and validation data loaders
    train_dataloader = get_train_dataloader(tokenizer, cfg)

    # Start the pre-training loop
    start_pretrainer(cfg, train_dataloader, tokenizer)
