import warnings
from dataclasses import InitVar, dataclass, field
from typing import List, Tuple  # Typing

import datasets
import nltk
import wandb
from wandb.wandb_run import Run  # Typing


@dataclass
class TableRow:
    predicted: str
    target: str
    source: str
    bleu: float = field(init=False)
    bertscore: float = field(init=False)

    # Attributes below are helpers and not logged in the table
    bleu_calculator: InitVar[datasets.metric.Metric] = None
    bertscore_calculator: InitVar[datasets.metric.Metric] = None

    def __post_init__(self, bleu_calculator, bertscore_calculator):
        self.bleu = bleu_calculator.compute(predictions=[nltk.word_tokenize(self.predicted)],
                                            references=[[nltk.word_tokenize(self.target)]])['bleu']
        self.bertscore = bertscore_calculator.compute(predictions=[self.predicted],
                                                      references=[self.target], lang="en")['f1'][0]

    def to_tuple(self):
        return self.predicted, self.target, self.source, self.bleu, self.bertscore

    @staticmethod
    def get_field_names_in_order() -> List[str]:
        """ There is hard coupling between this function and to_tuple above"""
        return ["Predicted", "Target", "Source", "BLEU", "BertScore"]


def create_inference_examples_table(run: Run, inferences_targets: List[List[str]], sources: List[str]) -> None:
    # Init wandb table
    inf_table = wandb.Table(columns=TableRow.get_field_names_in_order())

    # Create a list of [inference, target, source]
    zipped_inf_target_source = [[*inf_target, source]
                                for inf_target, source in zip(inferences_targets, sources)]

    # Initialize 🤗 datasets metrics
    bleu_calculator = datasets.load_metric('bleu', experiment_id="debug")
    bertscore_calculator = datasets.load_metric('bertscore', experiment_id="debug")

    # Populate the table
    for inference, target, source in zipped_inf_target_source:
        table_row = TableRow(inference, target, source,
                             bleu_calculator=bleu_calculator,
                             bertscore_calculator=bertscore_calculator)
        inf_table.add_data(*table_row.to_tuple())

    run.log({"inference_samples": inf_table})
