import argparse

from app.backend.inference import InferenceController
from config import cfg


def main():
    parser = argparse.ArgumentParser(description="Data2Text CMD.")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )
    args = parser.parse_args()

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.freeze()

    inference_controller = InferenceController(cfg)

    while True:
        input_table = input("Linearized table: ")
        print(inference_controller.inference(input_table))


if __name__ == '__main__':
    main()
