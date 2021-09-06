from collections import defaultdict
from dataclasses import InitVar, dataclass, field
from typing import Dict, List, Tuple  # Typing

import datasets
import nltk
import transformers
import wandb
from wandb.wandb_run import Run  # Typing

from visualizing.totto_table_parse import to_valid_html


@dataclass
class InferenceEvaluation:
    predicted: str
    target: str
    html_source: wandb.Html
    bleu: float = field(init=False)
    bertscore: float = field(init=False)
    source: str

    # Attributes below are helpers and not logged in the table
    tokenizer: InitVar[transformers.PreTrainedTokenizer] = None
    bleu_calculator: InitVar[datasets.metric.Metric] = None
    bertscore_calculator: InitVar[datasets.metric.Metric] = None

    def __post_init__(self, tokenizer, bleu_calculator, bertscore_calculator):
        self.bleu = bleu_calculator.compute(predictions=[tokenizer.tokenize(self.predicted)],
                                            references=[[tokenizer.tokenize(self.target)]])['bleu']
        self.bertscore = bertscore_calculator.compute(predictions=[self.predicted],
                                                      references=[self.target], lang="en")['f1'][0]

    def to_tuple(self):
        return self.predicted, self.target, self.html_source, self.bleu, self.bertscore, self.source

    @staticmethod
    def get_field_names_in_order() -> List[str]:
        """ There is hard coupling between this function and to_tuple above"""
        return ["Predicted", "Target", "HTML Source", "BLEU", "BertScore", "Source"]

    def get_float_metrics(self) -> Dict[str, float]:
        """ Returns the metrics that can be aggregated """
        return {"bleu": self.bleu, "bertscore": self.bertscore}


def create_inference_examples_table(inference_evaluations: List[InferenceEvaluation]):
    # Init wandb table
    inf_table = wandb.Table(columns=InferenceEvaluation.get_field_names_in_order())
    for table_row in inference_evaluations:
        inf_table.add_data(*table_row.to_tuple())

    return inf_table


def calculate_aggregated_metrics(inference_evaluations: List[InferenceEvaluation]) -> Dict[str, float]:
    aggregated_metrics_dict = defaultdict(int)
    for inference_eval in inference_evaluations:
        for metric, value in inference_eval.get_float_metrics().items():
            aggregated_metrics_dict[metric] += value

    return {k: v / len(inference_evaluations) for k, v in aggregated_metrics_dict.items()}


def create_inferences_evaluations(zipped_inf_target_source: List[List[str]],
                                  tokenizer: transformers.PreTrainedTokenizer) \
        -> List[InferenceEvaluation]:
    # Initialize 🤗 datasets metrics
    bleu_calculator = datasets.load_metric('bleu', experiment_id="debug")
    bertscore_calculator = datasets.load_metric('bertscore', experiment_id="debug")

    # Populate the table
    inference_evaluations = []
    for inference, target, source in zipped_inf_target_source:
        inference_eval = InferenceEvaluation(inference, target,
                                             wandb.Html(to_valid_html(source)),
                                             source,
                                             tokenizer=tokenizer,
                                             bleu_calculator=bleu_calculator,
                                             bertscore_calculator=bertscore_calculator)
        inference_evaluations.append(inference_eval)

    return inference_evaluations


def create_inference_report_on_wandb(run: Run, inferences_targets: List[List[str]],
                                     sources: List[str],
                                     tokenizer: transformers.PreTrainedTokenizer) -> None:
    # Create a list of [inference, target, source]
    zipped_inf_target_source = [[*inf_target, source]
                                for inf_target, source in zip(inferences_targets, sources)]
    inference_evaluations = create_inferences_evaluations(zipped_inf_target_source, tokenizer)

    # Generate the objects we want to log
    inference_examples_on_table = create_inference_examples_table(inference_evaluations)
    aggregated_metrics = calculate_aggregated_metrics(inference_evaluations)

    # Log the results on wandb
    run.log({"inference_samples": inference_examples_on_table})
    run.log(aggregated_metrics)
