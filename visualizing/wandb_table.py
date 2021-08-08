from typing import List, Tuple  # Typing

import wandb
from nlp import Metric, load_metric
from wandb.wandb_run import Run  # Typing


def calculate_inf_row(inference: str, target: str, source: str, metric: Metric) -> Tuple[str, str, str, float]:
    score = metric.compute([inference], [[target]])['bleu']

    return inference, target, source, score


def create_inference_examples_table(run: Run, inferences_targets: List[List[str]], sources: List[str]) -> None:
    inf_table = wandb.Table(columns=["Predicted", "Target", "Source", "BLEU"])
    bleu_metric = load_metric('bleu', experiment_id="evaluate")

    zipped_inf_target_source = [[*inf_target, source] for inf_target, source in zip(inferences_targets, sources)]

    for inference, target, source in zipped_inf_target_source:
        inf_table.add_data(*calculate_inf_row(inference, target, source, bleu_metric))

    run.log({"inference_samples": inf_table})
