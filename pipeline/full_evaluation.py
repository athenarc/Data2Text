"""
Takes as input a directory of config files and evaluates them. The results are
reported on wandb.
"""
import argparse
import subprocess
from pathlib import Path
from typing import List


def find_all_configs(root_dir: str) -> List[str]:
    paths = Path(root_dir).rglob('*.yaml')

    return [str(path) for path in paths]


def run_experiment(config_path: str) -> None:
    print("\n" + "=" * 120)
    print("=" * 120)
    subprocess.run(["python", "entry_point.py", "--config_file", f"{config_path}", "--job_type", "evaluate"],
                   check=True, )
    print("=" * 120)
    print("=" * 120 + "\n")


def exclude_or_include_configs(included: str, excluded: str, config_files: List[str]) -> List[str]:
    if included != "" and excluded != "":
        raise ValueError("One of the arguments --include, --exclude should NOT be given.")

    if included != "":
        filtered_paths = filter_paths(config_files, included, must_include=True)
    elif excluded != "":
        filtered_paths = filter_paths(config_files, excluded, must_include=False)
    else:
        filtered_paths = config_files

    return filtered_paths


def filter_paths(config_files, unfiltered: str, must_include: bool) -> List[str]:
    unfiltered_paths = unfiltered.strip().split(',')
    filtered_paths = filter(lambda config_file:
                            any(filter_file in config_file for filter_file in unfiltered_paths) == must_include,
                            config_files)

    return list(filtered_paths)


def print_final_config_paths(config_paths: List[str]) -> None:
    print(">>> Included config files:")
    for path in config_paths:
        print(f"\t- {path}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Full D2T experiment pipeline.")
    parser.add_argument(
        "--root_dir", required=True, help="path to the root of the config files", type=str
    )
    parser.add_argument(
        "--include", required=False, default="", help="run the evaluation only on the included configs (separated by ,)"
                                                      ", --exclude must be empty", type=str
    )
    parser.add_argument(
        "--exclude", required=False, default="", help="exclude the configs that include the param in their path "
                                                      "(separated by ,), --include must be empty", type=str
    )
    args = parser.parse_args()

    configs = find_all_configs(args.root_dir)
    filtered_configs = exclude_or_include_configs(args.include, args.exclude, configs)
    print_final_config_paths(filtered_configs)

    for config_path in filtered_configs:
        run_experiment(config_path)


if __name__ == '__main__':
    main()
