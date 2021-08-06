from transformers import T5Tokenizer

from data.build import get_train_dataloader, get_validation_dataloader
from engine.train import start_trainer


def train(cfg):
    # Get the T5 tokenizer
    tokenizer = T5Tokenizer.from_pretrained(cfg.MODEL.TOKENIZER_NAME)

    # Get train and validation data loaders
    train_dataloader = get_train_dataloader(tokenizer, cfg)
    validation_dataloader = get_validation_dataloader(tokenizer, cfg)

    # Start the training loop
    start_trainer(cfg, train_dataloader, validation_dataloader, tokenizer)
