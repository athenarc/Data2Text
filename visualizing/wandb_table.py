import warnings
from dataclasses import dataclass, field
from typing import List, Tuple  # Typing

import wandb
from nltk.translate.bleu_score import sentence_bleu
from wandb.wandb_run import Run  # Typing


@dataclass
class TableRow:
    predicted: str
    target: str
    source: str
    bleu: float = field(init=False)

    def to_tuple(self):
        return self.predicted, self.target, self.source, self.bleu

    def __post_init__(self):
        with warnings.catch_warnings():
            # Ignoring specific warning of calculating bleu on small sentences
            warnings.simplefilter("ignore")
            self.bleu = sentence_bleu([self.target], self.predicted)


def create_inference_examples_table(run: Run, inferences_targets: List[List[str]], sources: List[str]) -> None:
    inf_table = wandb.Table(columns=["Predicted", "Target", "Source", "BLEU"])

    zipped_inf_target_source = [[*inf_target, source] for inf_target, source in zip(inferences_targets, sources)]

    for inference, target, source in zipped_inf_target_source:
        table_row = TableRow(inference, target, source)
        inf_table.add_data(*table_row.to_tuple())

    run.log({"inference_samples": inf_table})
