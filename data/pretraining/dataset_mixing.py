import glob
import json
import random

from tqdm import tqdm


def datapoint_generator_creation(directory, prefix):
    def datapoint_generator(directory, prefix):
        files = glob.glob(f"{directory}/*")

        for file in files:
            with open(file, 'r') as inp:
                datapoints = json.load(inp)

            for datapoint in datapoints:
                # This is the format used when finetuning on ToTTo
                yield {
                    'subtable_and_metadata': f"{prefix}{datapoint['totto_task']}",
                    'final_sentence': datapoint['target']
                }

    return datapoint_generator(directory, prefix)


def prefix_creator(task_name: str) -> str:
    if task_name == "C4_MASKING_TASK_DIR":
        return "<c4_masking>"
    elif task_name == "WDC_COLUMN_MASKING":
        return "<wdc_masking>"
    elif task_name == "WDC_COLUMN_TYPE":
        return "<wdc_type>"
    elif task_name == "WDC_COLUMN_MIXING":
        return "<wdc_mixing>"
    elif task_name == "WDC_CONTENT_MASKING":
        return "<wdc_content>"


def create_dict_of_task_generators(dataset_paths):
    return {task: datapoint_generator_creation(dir_path, prefix_creator(task))
            for task, dir_path in dataset_paths.items()}


def mix_datasets():
    dataset_dir_paths = {
        'C4_MASKING_TASK_DIR': 'storage/datasets/c4/masked',
        'WDC_COLUMN_MASKING': 'storage/datasets/wdc/column_masking',
        'WDC_COLUMN_TYPE': 'storage/datasets/wdc/column_type',
        'WDC_COLUMN_MIXING': 'storage/datasets/wdc/column_mixing',
        'WDC_CONTENT_MASKING': 'storage/datasets/wdc/content_masking'
    }

    ratios = {
        'C4_MASKING_TASK_DIR': 0.2,
        'WDC_COLUMN_MASKING': 0.2,
        'WDC_COLUMN_TYPE': 0.2,
        'WDC_COLUMN_MIXING': 0.2,
        'WDC_CONTENT_MASKING': 0.2
    }

    OUTPUT_DIR = 'storage/datasets/pretrain/all_tasks'
    batches_numb = 1
    datapoints_per_file = 200_000

    task_generators = create_dict_of_task_generators(dataset_dir_paths)

    for which_batch in tqdm(range(batches_numb)):
        stored_datapoints = []
        for task, ratio in ratios.items():
            for _ in range(int(datapoints_per_file * ratio)):
                stored_datapoints.append(next(task_generators[task]))

        # Shuffle since the tasks are ordered
        random.shuffle(stored_datapoints)

        with open(f"{OUTPUT_DIR}/pretrain_file_{which_batch}.json", 'w') as outfile:
            json.dump(stored_datapoints, outfile)


if __name__ == '__main__':
    mix_datasets()
