import argparse
import os

import wandb
import yaml
from transformers import T5Tokenizer

from config import cfg
from data.build import get_train_dataloader, get_validation_dataloader
from engine.train import start_trainer
from utils.logger import setup_logger


def train(cfg):
    # Get the T5 tokenizer
    tokenizer = T5Tokenizer.from_pretrained(cfg.MODEL.TOKENIZER_NAME)

    # Get train and validation data loaders
    train_dataloader = get_train_dataloader(tokenizer, cfg)
    validation_dataloader = get_validation_dataloader(tokenizer, cfg)

    # Start the training loop
    start_trainer(cfg, train_dataloader, validation_dataloader, tokenizer)


def main():
    parser = argparse.ArgumentParser(description="Data2Text Model Training.")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )

    args = parser.parse_args()

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.freeze()

    logger = setup_logger("Data2Text logger", cfg.OUTPUT.LOGGER_DIR, cfg.MISC.LOGGER_LEVEL, 0)
    logger.info(args)

    logger.info(f"Running with config:\n{cfg}")

    # Read the wandb API key from secrets
    os.environ["WANDB_API_KEY"] = yaml.load(open('configs/secrets.yaml'),
                                            Loader=yaml.SafeLoader)['WANDB_API_KEY']

    # Initialization of the wandb for experiment orchestration
    wandb.init(project="data2text",
               dir=cfg.OUTPUT.WANDB_LOGS_DIR,
               name=cfg.WANDB.RUN_NAME,
               tags=cfg.WANDB.TAGS,
               mode=cfg.WANDB.MODE,
               notes=cfg.WANDB.NOTES,
               config=cfg)

    train(cfg)


if __name__ == '__main__':
    main()
