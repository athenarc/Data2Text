from torch.utils.data import DataLoader

from data.datasets_collection.totto.totto import Totto
from tools.enums import Mode

# from transformers import T5Tokenizer  # Typing
# from yacs.config import CfgNode  # Typing


def get_train_dataloader(tokenizer, cfg):
    return DataLoader(Totto(cfg, Mode.TRAIN, tokenizer),
                      batch_size=cfg.INPUT.TRAIN_BATCH_SIZE, shuffle=True,
                      num_workers=cfg.DATALOADER.NUM_WORKERS)


def get_validation_dataloader(tokenizer, cfg):
    return DataLoader(Totto(cfg, Mode.VALIDATION, tokenizer),
                      batch_size=cfg.INPUT.TEST_BATCH_SIZE, shuffle=False,
                      num_workers=cfg.DATALOADER.NUM_WORKERS)
