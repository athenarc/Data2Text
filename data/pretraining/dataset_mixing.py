import glob
import json
import random

from tqdm import tqdm


def datapoint_generator_creation(file_path, prefix):
    def datapoint_generator(file_path, prefix):
        with open(file_path, 'r') as inp:
            datapoints = json.load(inp)

        for datapoint in datapoints:
            # This is the format used when finetuning on ToTTo
            if 'subtable_and_metadata' in datapoint:
                yield datapoint
            else:
                yield {
                    'subtable_and_metadata': f"{prefix}{datapoint['task']}",
                    'final_sentence': datapoint['target']
                }

    return datapoint_generator(file_path, prefix)


def prefix_creator(task_name: str) -> str:
    if task_name == "TOTTO_ORIGINAL_TASK":
        return ""
    elif task_name == "TOTTO_COLUMN_MASKING":
        return "<erosion>"
    elif task_name == "TOTTO_COLUMN_ADDING":
        return "<erosion>"
    elif task_name == "TOTTO_COLUMN_MIXING":
        return "<erosion>"
    elif task_name == "TOTTO_VALUE_MASKING":
        return "<value>"


def create_dict_of_task_generators(dataset_paths):
    return {task: datapoint_generator_creation(dir_path, prefix_creator(task))
            for task, dir_path in dataset_paths.items()}


def mix_datasets():
    dataset_dir_paths = {
        'TOTTO_ORIGINAL_TASK': 'storage/datasets/compact_input/totto/train.json',
        'TOTTO_COLUMN_MIXING': 'storage/datasets/compact_input/pretrain_totto/tasks/column_mixing.json',
        'TOTTO_COLUMN_MASKING': 'storage/datasets/compact_input/pretrain_totto/tasks/column_masking.json',
        'TOTTO_COLUMN_ADDING': 'storage/datasets/compact_input/pretrain_totto/tasks/added_columns.json',
        'TOTTO_VALUE_MASKING': 'storage/datasets/compact_input/pretrain_totto/tasks/value_masking.json'
    }

    ratios = {
        'TOTTO_ORIGINAL_TASK': 0.2,
        'TOTTO_COLUMN_MIXING': 0.2,
        'TOTTO_COLUMN_MASKING': 0.2,
        'TOTTO_COLUMN_ADDING': 0.2,
        'TOTTO_VALUE_MASKING': 0.2
    }

    OUTPUT_DIR = 'storage/datasets/compact_input/pretrain_totto/combined'
    batches_numb = 1
    datapoints_per_file = 400_000

    task_generators = create_dict_of_task_generators(dataset_dir_paths)

    for which_batch in tqdm(range(batches_numb)):
        stored_datapoints = []
        for task, ratio in ratios.items():
            for _ in range(int(datapoints_per_file * ratio)):
                try:
                    stored_datapoints.append(next(task_generators[task]))
                except StopIteration:
                    print(task, _)
                    raise StopIteration

        # Shuffle since the tasks are ordered
        random.shuffle(stored_datapoints)

        with open(f"{OUTPUT_DIR}/totto_auxiliary_tasks_file_{which_batch}.json", 'w') as outfile:
            json.dump(stored_datapoints, outfile)


if __name__ == '__main__':
    mix_datasets()
