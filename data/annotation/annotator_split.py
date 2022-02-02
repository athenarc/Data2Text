import random


def create_overlapping_annotations(annotation_split, annotators, annot_per_point):
    for datapoint in annotation_split:
        datapoint['annotator'] = ', '.join(random.sample(annotators, annot_per_point))

    return annotation_split


def split_dataset(datapoints, overlap_ratio):
    shuffled = random.sample(datapoints, len(datapoints))

    return shuffled[:int(overlap_ratio * len(shuffled))], datapoints[int(overlap_ratio * len(shuffled)):]


def assign_annotators(datapoints, annotators, overlap_ratio):
    overlap_dataset, single_annot_dataset = split_dataset(datapoints, overlap_ratio)

    # Assign annotators to the overlap portion of the dataset
    overlap_dataset = create_overlapping_annotations(overlap_dataset, annotators, annot_per_point=3)

    # Assign annotators to the non overlap portion of the dataset
    for datapoint in single_annot_dataset:
        datapoint['annotator'] = 'empty'

    dataset_with_annotators = overlap_dataset + single_annot_dataset
    random.shuffle(dataset_with_annotators)

    return dataset_with_annotators
