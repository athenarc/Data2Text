import random
import string
from collections import defaultdict
from dataclasses import InitVar, dataclass, field
from typing import Dict, List, Tuple  # Typing

import datasets
import transformers
import wandb
from tqdm import tqdm
from wandb.wandb_run import Run  # Typing

from visualizing.gruen.gruen_calculation import Gruen
from visualizing.parent.parent_calc import parent_calc
from visualizing.parent.table_process import tables_to_parent_format
from visualizing.totto_table_parse import to_valid_html


@dataclass
class InferenceEvaluation:
    predicted: str
    targets: List[str]
    html_source: wandb.Html
    bleu: float = field(init=False)
    bertscore: float = field(init=False)
    parent: float = field(init=False)
    gruen: float = field(init=False)
    source: str

    # Attributes below are helpers and not logged in the table
    tokenizer: InitVar[transformers.PreTrainedTokenizer] = None
    bleu_calculator: InitVar[datasets.metric.Metric] = None
    bertscore_calculator: InitVar[datasets.metric.Metric] = None
    gruen_calculator: InitVar[Gruen] = None

    def __post_init__(self, tokenizer, bleu_calculator, bertscore_calculator, gruen_calculator):
        self.bleu = bleu_calculator.compute(predictions=[tokenizer.tokenize(self.predicted)],
                                            references=[[tokenizer.tokenize(targets) for targets in self.targets]])[
            'bleu']

        self.bertscore = bertscore_calculator.compute(predictions=[self.predicted],
                                                      references=[self.targets], lang="en")['f1'][0]

        try:
            _, _, self.parent, _ = parent_calc(predictions=[self.predicted.lower().split()],
                                               references=[target.lower().split() for target in self.targets],
                                               tables=tables_to_parent_format([self.source]))
        except ValueError:
            self.parent = -1

        try:
            self.gruen = gruen_calculator.compute(predictions=[self.predicted])[0]
        except ValueError:
            self.gruen = -1

    def to_tuple(self):
        return self.predicted, " | ".join(self.targets), \
               self.html_source, self.bleu, self.bertscore, \
               self.parent, self.gruen, self.source

    @staticmethod
    def get_field_names_in_order() -> List[str]:
        """ There is hard coupling between this function and to_tuple above"""
        return ["Predicted", "Target", "HTML Source", "BLEU", "BertScore", "PARENT", "GRUEN", "Source"]

    def get_float_metrics(self) -> Dict[str, float]:
        """ Returns the metrics that can then be aggregated """
        return {"bleu": self.bleu, "bertscore": self.bertscore, "PARENT": self.parent, "GRUEN": self.gruen}


def create_inference_examples_table(inference_evaluations: List[InferenceEvaluation]):
    # Init wandb table
    inf_table = wandb.Table(columns=InferenceEvaluation.get_field_names_in_order())
    for table_row in inference_evaluations:
        inf_table.add_data(*table_row.to_tuple())

    return inf_table


def calculate_aggregated_metrics(inference_evaluations: List[InferenceEvaluation]) -> Dict[str, float]:
    aggregated_metrics_dict = defaultdict(lambda: [0, 0])  # Sum of statistic, population

    # We skip all the datapoints that the metric failed to be calculated
    for inference_eval in inference_evaluations:
        for metric, value in inference_eval.get_float_metrics().items():
            aggregated_metrics_dict[metric][0] += value if value != -1 else 0  # Metric value
            aggregated_metrics_dict[metric][1] += 1 if value != -1 else 0  # Population

    return {k: v[0] / v[1] for k, v in aggregated_metrics_dict.items()}


def create_inferences_evaluations(zipped_inf_targets_source: List[Tuple[str, List[str], str]],
                                  tokenizer: transformers.PreTrainedTokenizer) \
        -> List[InferenceEvaluation]:
    # Initialize 🤗 datasets metrics
    bleu_calculator = datasets.load_metric('bleu', experiment_id=''.join(random.choice(string.ascii_letters)
                                                                         for _ in range(10)))
    bertscore_calculator = datasets.load_metric('bertscore', experiment_id=''.join(random.choice(string.ascii_letters)
                                                                                   for _ in range(10)))

    # Read COLA model used for GRUEN
    gruen_calculator = Gruen('storage/checkpoints/metrics/cola/')

    inference_evaluations = []
    for inference, targets, source in tqdm(zipped_inf_targets_source, desc="Metric calculation:"):
        inference_eval = InferenceEvaluation(inference, targets,
                                             wandb.Html(to_valid_html(source)),
                                             source,
                                             tokenizer=tokenizer,
                                             bleu_calculator=bleu_calculator,
                                             bertscore_calculator=bertscore_calculator,
                                             gruen_calculator=gruen_calculator)
        inference_evaluations.append(inference_eval)

    return inference_evaluations


def create_inference_report_on_wandb(run: Run, inferences: List[str], targets: List[List[str]],
                                     sources: List[str],
                                     tokenizer: transformers.PreTrainedTokenizer) -> None:
    # Create a list of (inference, targets, source)
    zipped_inf_targets_source = list(zip(inferences, targets, sources))
    inference_evaluations = create_inferences_evaluations(zipped_inf_targets_source, tokenizer)

    # Table example inferences on a sample of the first 100 datapoints
    sample_inferences_stored = inference_evaluations[:min(400, len(inference_evaluations))]
    inference_examples_on_table = create_inference_examples_table(sample_inferences_stored)

    # Aggregated metrics on the whole evaluation set
    aggregated_metrics = calculate_aggregated_metrics(inference_evaluations)

    # Log the results on wandb
    run.log({"inference_samples": inference_examples_on_table})
    run.log(aggregated_metrics)
