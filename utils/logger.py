import logging
import os
import sys


def setup_logger(name, save_dir, level_str, distributed_rank):
    if level_str == "NOTSET":
        level = logging.NOTSET
    elif level_str == "DEBUG":
        level = logging.DEBUG
    elif level_str == "INFO":
        level = logging.INFO
    elif level_str == "WARNING":
        level = logging.WARNING
    elif level_str == "ERROR":
        level = logging.ERROR
    elif level_str == "CRITICAL":
        level = logging.CRITICAL
    else:
        raise ValueError("Logger level is not valid, valid levels: "
                         "https://docs.python.org/3/library/logging.html#levels")
    logger = logging.getLogger(name)

    logger.setLevel(level)

    # don't log results for the non-master process
    if distributed_rank > 0:
        return logger
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if save_dir:
        fh = logging.FileHandler(os.path.join(save_dir, "log.txt"), mode='w')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
