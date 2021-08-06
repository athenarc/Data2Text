import logging

import pytorch_lightning as pl
import torch
from pytorch_lightning import loggers as pl_loggers
from pytorch_lightning.callbacks import ModelCheckpoint

from modeling.T5Module import T5System


def start_trainer(cfg, train_dataloader, validation_dataloader, tokenizer):
    model = T5System(cfg, tokenizer)

    # Callbacks
    checkpoint = ModelCheckpoint(dirpath=cfg.OUTPUT.CHECKPOINTS_DIR, monitor="val_loss",
                                 save_top_k=4, every_n_epochs=cfg.SOLVER.CHECKPOINT_PERIOD)

    # Set directory that wandb will store its runs
    wandb_logger = pl_loggers.WandbLogger(save_dir=f"{cfg.OUTPUT.WANDB_LOGS_DIR}wandb/")

    # Check if there is a (or more) GPU available
    gpus_numb = min([cfg.MODEL.GPUS_NUMB, torch.cuda.device_count()])
    if gpus_numb == 0:
        logging.warning("Not using a GPU. Training will be slow.")

    trainer = pl.Trainer(max_epochs=cfg.SOLVER.MAX_EPOCHS,
                         callbacks=[checkpoint], gpus=cfg.MODEL.GPUS_NUMB,
                         logger=wandb_logger, log_every_n_steps=cfg.SOLVER.LOG_PERIOD)

    trainer.fit(model,
                train_dataloaders=train_dataloader,
                val_dataloaders=validation_dataloader)
