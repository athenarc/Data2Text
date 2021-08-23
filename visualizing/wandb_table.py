from dataclasses import InitVar, dataclass, field
from typing import List, Tuple  # Typing

import datasets
import nltk
import transformers
import wandb
from wandb.wandb_run import Run  # Typing

from visualizing.totto_table_parse import to_valid_html


@dataclass
class TableRow:
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


def create_inference_examples_table(run: Run, inferences_targets: List[List[str]],
                                    sources: List[str], tokenizer: transformers.PreTrainedTokenizer) -> None:
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
        table_row = TableRow(inference, target,
                             wandb.Html(to_valid_html(source)),
                             source,
                             tokenizer=tokenizer,
                             bleu_calculator=bleu_calculator,
                             bertscore_calculator=bertscore_calculator)
        inf_table.add_data(*table_row.to_tuple())

    run.log({"inference_samples": inf_table})
