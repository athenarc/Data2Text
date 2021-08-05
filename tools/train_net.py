import argparse
import os
import wandb
import sys
from os import mkdir

from config import cfg
from utils.logger import setup_logger


def train():
    pass


def main():
    parser = argparse.ArgumentParser(description="Data2Text Model Training.")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )

    args = parser.parse_args()

    num_gpus = int(os.environ["WORLD_SIZE"]) if "WORLD_SIZE" in os.environ else 1

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.freeze()

    logger = setup_logger("Data2Text logger", cfg.OUTPUT.LOGGER_DIR, cfg.MISC.LOGGER_LEVEL, 0)
    logger.info(f"Using {num_gpus} GPUS")
    logger.info(args)

    if args.config_file != "":
        logger.info("Loaded configuration file {}".format(args.config_file))
        with open(args.config_file, 'r') as cf:
            config_str = "\n" + cf.read()
            logger.info(config_str)

    logger.info(f"Running with config:\n{cfg}")

    # Initialization of the wandb for experiment orchestration
    wandb.init(project="data2text",
               dir=cfg.OUTPUT.WANDB_LOGS_DIR,
               name=cfg.WANDB.RUN_NAME,
               tags=cfg.WANDB.TAGS,
               config=cfg)


if __name__ == '__main__':
    main()
