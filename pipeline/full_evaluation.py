"""
Takes as input a directory of config files and evaluates them. The results are
reported on wandb.
"""
import argparse
import subprocess
from pathlib import Path


def find_all_configs(root_dir):
    paths = Path(root_dir).rglob('*.yaml')

    return list(paths)


def run_experiment(config_path):
    print("\n" + "=" * 120)
    print("=" * 120)
    subprocess.run(["python", "entry_point.py", "--config_file",  f"{config_path}", "--job_type", "evaluate"],
                   check=True, )
    print("=" * 120)
    print("=" * 120 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Full D2T experiment pipeline.")
    parser.add_argument(
        "--root_dir", required=True, help="path to the root of the config files", type=str
    )
    args = parser.parse_args()

    configs = find_all_configs(args.root_dir)
    for config_path in configs:
        run_experiment(config_path)


if __name__ == '__main__':
    main()
