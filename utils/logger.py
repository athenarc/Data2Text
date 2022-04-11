import logging
import os
import subprocess as sp
import sys

global_logger = None


class LoggerLevelNotFound(KeyError):
    pass


def setup_logger(name: str, save_dir: str, level_str: str, distributed_rank: int) -> logging.Logger:
    levels = {
        "NOTSET": logging.NOTSET,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    try:
        level = levels[level_str]
    except KeyError:
        raise LoggerLevelNotFound(f"Logger level {level_str} is not valid, valid levels: "
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

    global global_logger
    global_logger = logger

    return logger


def return_gpu_memory():
    command = "nvidia-smi --query-gpu=memory.free --format=csv"
    memory_free_info = sp.check_output(command.split()).decode('ascii').split('\n')[:-1][1:]
    memory_free_values = [str(int(x.split()[0])) for i, x in enumerate(memory_free_info)]
    memory_free_values_str = ' | '.join(memory_free_values)
    return memory_free_values_str
