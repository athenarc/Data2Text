import random
from collections import defaultdict


def create_overlapping_annotations(annotation_split, annotators, annot_per_point):
    annotated_benchmarks = defaultdict(lambda: [])
    for datapoint in annotation_split:
        chosen_annotators = random.sample(annotators, annot_per_point)
        for annotator in chosen_annotators:
            annotated_benchmarks[annotator].append(datapoint)

    return annotated_benchmarks


def split_dataset(datapoints, overlap_ratio):
    shuffled = random.sample(datapoints, len(datapoints))

    return shuffled[:int(overlap_ratio * len(shuffled))], datapoints[int(overlap_ratio * len(shuffled)):]


def assign_annotators(datapoints, annotators, overlap_ratio):
    # Add an id attribute
    for ind, datapoint in enumerate(datapoints):
        datapoint['id'] = ind

    overlap_dataset, _ = split_dataset(datapoints, overlap_ratio)

    # Assign annotators to the overlap portion of the dataset
    overlap_dataset = create_overlapping_annotations(overlap_dataset, annotators, annot_per_point=2)

    # Assign annotators to the non overlap portion of the dataset
    # for datapoint in single_annot_dataset:
    #     overlap_dataset['Mike'].append(datapoint)

    return overlap_dataset
