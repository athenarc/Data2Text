import argparse
import os

import wandb
import yaml

from config import cfg
from tools.evaluate_net import evaluate
from tools.pretrain_net import pretrain
from tools.train_net import train
from utils.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description="Data2Text Model Training.")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )
    parser.add_argument(
        "--job_type", default="train", help="train or eval", type=str
    )
    args = parser.parse_args()

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.freeze()

    # Setup the logger and output config info
    logger = setup_logger("Data2Text logger", cfg.OUTPUT.LOGGER_DIR, cfg.MISC.LOGGER_LEVEL, 0)
    logger.info(args)
    logger.info(f"Running with config:\n{cfg}")
    logger.info(f"Running in {args.job_type} mode.")

    # Read the wandb API key from secrets
    os.environ["WANDB_API_KEY"] = yaml.load(open('configs/secrets.yaml'),
                                            Loader=yaml.SafeLoader)['WANDB_API_KEY']

    # Initialization of the wandb for experiment orchestration
    run = wandb.init(project="data2text",
                     job_type=args.job_type,
                     group=cfg.WANDB.GROUP,
                     dir=cfg.OUTPUT.WANDB_LOGS_DIR,
                     name=cfg.WANDB.RUN_NAME,
                     tags=cfg.WANDB.TAGS,
                     mode=cfg.WANDB.MODE,
                     notes=cfg.WANDB.NOTES,
                     config=cfg
                     )

    if args.job_type == "train":
        train(cfg)
    elif args.job_type == "evaluate":
        evaluate(cfg, run)
    elif args.job_type == "pretrain":
        pretrain(cfg)



if __name__ == '__main__':
    main()
