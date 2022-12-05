import asyncio
import json
import logging
import random
from datetime import date

import numpy as np
import pandas as pd
from tqdm import tqdm

from app.backend.db.PostgresController import PostgresController
from data.annotation_cordis.inode_cordis_db_query import gather_annotation_info
from data.annotation_qr2t.annotator_split import create_overlapping_annotations

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)




async def create_annotation_points(file_path):
    db_controller = PostgresController()
    semaphore = asyncio.Semaphore(5)

    df = pd.read_csv(file_path)
    annotation_points = []

    for _, datapoint in tqdm(list(df.iterrows()), total=len(df), desc=file_path.split('/')[-1]):
        async with semaphore:
            res = await gather_annotation_info(datapoint['sql_query'], db_controller)
            if res is not None:
                annotation_points.append(
                    {
                        'nl_query': datapoint['question'],
                        'inference': res
                    }
                )

    return annotation_points


def assign_annotators(datapoints, annotators, annot_per_point, start_id_index):
    # Add an id attribute
    for ind, datapoint in enumerate(datapoints):
        datapoint['id'] = ind + start_id_index

    # Assign annotators to the overlap portion of the dataset
    # Could be used for evaluation
    overlap_dataset = create_overlapping_annotations(datapoints, annotators, annot_per_point)

    return overlap_dataset


async def create_cordis_inode_for_annotation(annotators):
    train_points = await create_annotation_points('storage/datasets/cordis_inode/original/train.csv')
    dev_points = await create_annotation_points('storage/datasets/cordis_inode/original/dev.csv')
    test_points = await create_annotation_points('storage/datasets/cordis_inode/original/test.csv')

    dev_points = dev_points + test_points

    train_points_with_annotators = assign_annotators(train_points, annotators, 1, 0)
    dev_points_with_annotators = assign_annotators(dev_points, annotators, 3, len(train_points))

    for key in train_points_with_annotators:
        dev_points_with_annotators[key] += train_points_with_annotators[key]
        random.shuffle(dev_points_with_annotators[key])

    class NpEncoder(json.JSONEncoder):
        """ Needed to encode dictionary fields with numpy types """
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, date):
                return str(date)
            return super(NpEncoder, self).default(obj)

    for annotator, benchmark in dev_points_with_annotators.items():
        with open('storage/datasets/cordis_inode/original/label_studio/not_labelled/' + annotator + '.json', 'w') \
                as outfile:
            json.dump(benchmark, outfile, cls=NpEncoder)


if __name__ == '__main__':
    annotators = [
        "Stavroula",
        "George",
        "Chris",
        "Katerina",
        "Antonis",
        "Anna",
        "Mike"
    ]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_cordis_inode_for_annotation(annotators))
