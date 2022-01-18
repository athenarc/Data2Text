import logging

import pytorch_lightning as pl
import torch
from pytorch_lightning import loggers as pl_loggers
from pytorch_lightning.callbacks import ModelCheckpoint
from torch.utils.data import DataLoader  # Typing
from transformers import T5Tokenizer  # Typing
from yacs.config import CfgNode  # Typing

from modeling.T5Module import T5System


def start_pretrainer(cfg: CfgNode, train_dataloader: DataLoader, tokenizer: T5Tokenizer) -> None:
    # Continue from checkpoint or start from scratch
    if cfg.MODEL.PATH_TO_CHECKPOINT != "":
        model = T5System.load_from_checkpoint(cfg.MODEL.PATH_TO_CHECKPOINT,
                                              cfg=cfg, tokenizer=tokenizer)
    else:
        model = T5System(cfg, tokenizer)

    # Callbacks
    checkpoint = ModelCheckpoint(dirpath=cfg.OUTPUT.CHECKPOINTS_DIR, monitor="train_loss",
                                 save_top_k=4, every_n_train_steps=cfg.SOLVER.CHECKPOINT_PERIOD)

    # Set directory that wandb will store its runs
    wandb_logger = pl_loggers.WandbLogger(save_dir=f"{cfg.OUTPUT.WANDB_LOGS_DIR}wandb/")

    # Check if there is a (or more) GPU available
    gpus_numb = min([cfg.MODEL.GPUS_NUMB, torch.cuda.device_count()])
    if gpus_numb == 0:
        logging.warning("Not using a GPU. Pre-training will be slow.")

    trainer = pl.Trainer(max_epochs=cfg.SOLVER.MAX_EPOCHS,
                         callbacks=[checkpoint], gpus=cfg.MODEL.GPUS_NUMB,
                         logger=wandb_logger, log_every_n_steps=cfg.SOLVER.LOG_PERIOD)

    trainer.fit(model,
                train_dataloaders=train_dataloader)
