from typing import Any, Dict, List, Optional  # Typing

import numpy as np
import pytorch_lightning as pl
import torch
from nlp import Metric, load_metric
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers.modeling_outputs import Seq2SeqModelOutput  # Typing
from yacs.config import CfgNode  # Typing

from utils.model import ids_to_clean_text

# class T5(torch.nn.Module):
#     def __init__(self, cfg):
#         super(T5, self).__init__()
#
#         self.T5_encoder_decoder = T5ForConditionalGeneration\
#             .from_pretrained(cfg.MODEL.PRETRAINED_MODEL_NAME)
#
#     def forward(
#             self, input_ids, attention_mask=None, decoder_input_ids=None,
#             decoder_attention_mask=None, lm_labels=None
#     ):
#         return self.T5_encoder_decoder()


class T5System(pl.LightningModule):
    def __init__(self, cfg: CfgNode, tokenizer: T5Tokenizer):
        super().__init__()
        self.model: T5ForConditionalGeneration = T5ForConditionalGeneration.from_pretrained(cfg.MODEL.PRETRAINED_MODEL_NAME)
        self.lr: float = cfg.SOLVER.BASE_LR
        self.max_generated_size: int = cfg.MODEL.MAX_OUTPUT_TOKENS
        self.tokenizer: T5Tokenizer = tokenizer
        self.bleu_metric: Metric = load_metric('bleu')

    def _step(self, batch: Dict[str, Any]) -> float:
        # In order for our T5 model to return a loss we must pass labels
        labels = batch["target_ids"]

        # Label the padding with -100 so as to be ignored when calculating the loss
        labels[labels[:, :] == self.tokenizer.pad_token_id] = -100

        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            labels=labels,
            decoder_attention_mask=batch['target_mask']
        )

        loss = outputs[0]
        return loss

    def _generative_step(self, batch: Dict[str, Any]) -> Dict[str, float]:

        generated_ids = self.model.generate(
            batch["source_ids"],
            attention_mask=batch["source_mask"],
            use_cache=True,
            decoder_attention_mask=batch['target_mask'],
            max_length=self.max_generated_size,
            num_beams=2,
            repetition_penalty=2.5,
            length_penalty=1.0,
            early_stopping=True
        )
        preds = ids_to_clean_text(self.tokenizer, generated_ids)
        target = ids_to_clean_text(self.tokenizer, batch["target_ids"])

        loss = self._step(batch)

        # Transform target since BLEU expects a list of a list of candidate references
        target = list(map(lambda x: [x], target))
        bleu_score = self.bleu_metric.compute(preds, target)['bleu']

        gen_len = np.mean(list(map(len, generated_ids)))

        base_metrics = {'val_loss': loss, "bleu": bleu_score}
        base_metrics.update(gen_len=gen_len, preds=preds)

        return base_metrics

    def forward(
            self, input_ids: List[List[int]],
            attention_mask: Optional[List[List[int]]] = None,
            decoder_input_ids: Optional[List[List[int]]] = None,
            decoder_attention_mask: Optional[List[List[int]]] = None,
            labels: Optional[List[List[int]]] = None
    ) -> Seq2SeqModelOutput:
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels,
        )

    def training_step(self, batch: Dict[str, Any], batch_idx: int) -> Dict[str, float]:
        loss = self._step(batch)
        self.log('train_loss', loss)
        return {"loss": loss}

    def validation_step(self, batch: Dict[str, Any], batch_idx: int) -> Dict[str, float]:
        base_metrics = self._generative_step(batch)
        self.log('val_loss', base_metrics['val_loss'], on_epoch=True, prog_bar=True)
        self.log('bleu', base_metrics['bleu'], on_epoch=True)

        return base_metrics

    def configure_optimizers(self) -> torch.optim.Optimizer:
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer
