import argparse
import os

import wandb
import yaml

from config import cfg
from tools.train_net import train
from utils.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description="Data2Text Model Training.")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )
    args = parser.parse_args()

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.freeze()

    # Setup the logger and output config info
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
