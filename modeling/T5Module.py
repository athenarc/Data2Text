import pytorch_lightning as pl
import torch
from transformers import T5ForConditionalGeneration

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
    def __init__(self, cfg, tokenizer):
        super().__init__()
        self.model = T5ForConditionalGeneration.from_pretrained(cfg.MODEL.PRETRAINED_MODEL_NAME)
        self.lr = cfg.SOLVER.BASE_LR
        self.tokenizer = tokenizer

    def _step(self, batch):
        # In order for our T5 model to return a loss we must pass lm_labels
        lm_labels = batch["target_ids"]

        # Label the padding with -100 so as to be ignored
        lm_labels[lm_labels[:, :] == self.tokenizer.pad_token_id] = -100

        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            lm_labels=lm_labels,
            decoder_attention_mask=batch['target_mask']
        )

        loss = outputs[0]
        return loss

    def forward(
            self, input_ids, attention_mask=None, decoder_input_ids=None,
            decoder_attention_mask=None, lm_labels=None
    ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=lm_labels,
        )

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)

        # wandb_logs = {"train_loss": loss}
        self.log('train_loss', loss)
        return {"loss": loss}


    # def validation_step(self, batch, batch_idx):
    #     loss = self._step(batch)
    #     self.log("val_loss", loss)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer
