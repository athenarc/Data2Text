import random
from collections import Counter, defaultdict


def create_overlapping_annotations(annotation_split, annotators, annot_per_point):
    annotated_benchmarks = defaultdict(lambda: [])
    for datapoint in annotation_split:
        chosen_annotators = random.sample(annotators, annot_per_point)
        for annotator in chosen_annotators:
            annotated_benchmarks[annotator].append(datapoint)

    return annotated_benchmarks


def split_dataset(datapoints, overlap_ratio):
    shuffled = random.sample(datapoints, len(datapoints))

    return shuffled[:int(overlap_ratio * len(shuffled))], shuffled[int(overlap_ratio * len(shuffled)):]


def assign_annotators(datapoints, annotators, overlap_ratio):
    # Add an id attribute
    for ind, datapoint in enumerate(datapoints):
        datapoint['id'] = ind

    overlap_dataset, single_annotation = split_dataset(datapoints, overlap_ratio)

    # Assign annotators to the overlap portion of the dataset
    # Could be used for evaluation
    overlap_dataset = create_overlapping_annotations(overlap_dataset, annotators, annot_per_point=3)

    # Assign annotators for the single annotator portion of the dataset
    single_annotation = create_overlapping_annotations(single_annotation, annotators, annot_per_point=1)

    # Combine the two dicts of lists
    for key, value in overlap_dataset.items():
        value.extend(single_annotation[key])
        random.shuffle(value)

    # Assign annotators to the non overlap portion of the dataset
    # for datapoint in single_annot_dataset:
    #     overlap_dataset['Mike'].append(datapoint)

    return overlap_dataset


def confirm_overlap(final_benchmark):
    datapoint_population = defaultdict(lambda: 0)

    for _, datapoints in final_benchmark.items():
        for datapoint in datapoints:
            datapoint_population[datapoint['id']] += 1

    return Counter(datapoint_population.values())
