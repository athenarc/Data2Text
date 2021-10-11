import argparse

import yaml


def read_settings_file():
    parser = argparse.ArgumentParser(description="Streamlit D2T App.")
    parser.add_argument(
        "config_file", help="path to config file", type=str
    )
    args = parser.parse_args()

    with open(args.config_file) as file:
        settings = yaml.full_load(file)

    return settings
