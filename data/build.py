from torch.utils.data import DataLoader
from data.datasets.totto.totto import Totto


def get_train_dataloader(tokenizer, cfg):
    return DataLoader(Totto(cfg, "train", tokenizer),
                      batch_size=cfg.INPUT.SIZE_TRAIN, shuffle=True)


def get_validation_dataloader(tokenizer, cfg):
    return DataLoader(Totto(cfg, "validation", tokenizer),
                      batch_size=cfg.INPUT.SIZE_TEST, shuffle=True)
