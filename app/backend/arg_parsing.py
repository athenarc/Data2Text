import argparse

from config import cfg


def get_model_config(name: str = ""):
    parser = argparse.ArgumentParser(description="Data2Text CMD.")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )
    args = parser.parse_args()

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.freeze()

    return cfg
