import copy
import json
import glob
from tqdm import tqdm

from absl import app
from absl import flags

from data.datasets.totto import utils as preprocess_utils

import six

flags.DEFINE_string("input_dir_path", "storage/datasets/totto/linearized/", "Input dir containing totto raw files.")

flags.DEFINE_string("output_dir_path", "storage/datasets/totto/filtered/",
                    "Output dir that linearized tables will be stored.")

# flags.DEFINE_integer("examples_to_visualize", 100,
#                      "Number of examples to visualize.")

FLAGS = flags.FLAGS


def _generate_processed_examples(input_path):
    """Generate TF examples."""
    processed_json_examples = []

    with open(input_path) as f:
        lines_numb = sum(1 for _ in f)

    with open(input_path, "r", encoding="utf-8") as input_file:
        for line in tqdm(input_file, total=lines_numb):
            line = six.ensure_text(line, "utf-8")
            json_example = json.loads(line)
            table = json_example["table"]
            table_page_title = json_example["table_page_title"]
            table_section_title = json_example["table_section_title"]
            cell_indices = json_example["highlighted_cells"]

            subtable = (
                preprocess_utils.get_highlighted_subtable(
                    table=table,
                    cell_indices=cell_indices,
                    with_heuristic_headers=True))

            # Table strings without page and section title.
            full_table_str = preprocess_utils.linearize_full_table(
                table=table,
                cell_indices=cell_indices,
                table_page_title=None,
                table_section_title=None)

            subtable_str = (
                preprocess_utils.linearize_subtable(
                    subtable=subtable,
                    table_page_title=None,
                    table_section_title=None))

            full_table_metadata_str = (
                preprocess_utils.linearize_full_table(
                    table=table,
                    cell_indices=cell_indices,
                    table_page_title=table_page_title,
                    table_section_title=table_section_title))

            subtable_metadata_str = (
                preprocess_utils.linearize_subtable(
                    subtable=subtable,
                    table_page_title=table_page_title,
                    table_section_title=table_section_title))

            processed_json_example = copy.deepcopy(json_example)
            processed_json_example["full_table_str"] = full_table_str
            processed_json_example["subtable_str"] = subtable_str
            processed_json_example[
                "full_table_metadata_str"] = full_table_metadata_str
            processed_json_example["subtable_metadata_str"] = subtable_metadata_str
            processed_json_examples.append(processed_json_example)

    return processed_json_examples


def create_raw_files(_):
    input_dir_path = FLAGS.input_dir_path
    output_dir_path = FLAGS.output_dir_path
    file_substrings = ["train", "dev", "test"]

    for file_str in file_substrings:
        try:
            input_path = glob.glob(f'{input_dir_path}*{file_str}*')[0]
            print(f">>> Processing {file_str} file.")
        except IndexError:
            print(f"No {file_str} file found. Skipping...")
            continue
        output_path = f"{output_dir_path}{file_str}.json"

        processed_json_examples = _generate_processed_examples(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("[")
            first_flag = True
            for json_example in processed_json_examples:
                if not first_flag:
                    f.write(",\n")
                else:
                    first_flag = False
                f.write(json.dumps(json_example))
            f.write("]")


def filter_subtable_metadata_final_sent(_):
    input_dir_path = FLAGS.input_dir_path
    output_dir_path = FLAGS.output_dir_path
    file_substrings = ["train", "dev"]

    for file_str in file_substrings:
        filtered_datapoints = []
        try:
            input_path = glob.glob(f'{input_dir_path}*{file_str}*')[0]
            print(f">>> Processing {file_str} file.")
        except IndexError:
            print(f"No {file_str} file found. Skipping...")
            continue
        output_path = f"{output_dir_path}{file_str}.json"

        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)

        # with open(input_path, "r", encoding="utf-8") as input_file:
        for datapoint in tqdm(data):
            for annotation in datapoint['sentence_annotations']:
                filtered_datapoints.append({
                    "subtable_and_metadata": datapoint['subtable_metadata_str'],
                    "final_sentence": annotation['final_sentence']
                })

        with open(output_path, 'w') as outfile:
            json.dump(filtered_datapoints, outfile)


if __name__ == "__main__":
    app.run(filter_subtable_metadata_final_sent)
