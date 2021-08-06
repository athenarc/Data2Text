from torch.utils.data import DataLoader

from data.datasets.totto.totto import Totto


def get_train_dataloader(tokenizer, cfg):
    return DataLoader(Totto(cfg, "train", tokenizer),
                      batch_size=cfg.INPUT.TRAIN_BATCH_SIZE, shuffle=True,
                      num_workers=cfg.DATALOADER.NUM_WORKERS)


def get_validation_dataloader(tokenizer, cfg):
    return DataLoader(Totto(cfg, "validation", tokenizer),
                      batch_size=cfg.INPUT.TEST_BATCH_SIZE, shuffle=False,
                      num_workers=cfg.DATALOADER.NUM_WORKERS)
