import torch
import transformers.optimization


def get_adam_optimizer(parameters, lr):
    return torch.optim.Adam(parameters, lr=lr)


def get_ada_factor_optimizer(parameters, lr):
    """
    Suggested parameters for fine-tuning T5.
    Sources:
    * https://huggingface.co/transformers/main_classes/optimizer_schedules.html#adafactor-pytorch
    * https://discuss.huggingface.co/t/t5-finetuning-tips
     """
    return transformers.optimization \
        .Adafactor(parameters, lr,
                   eps=(1e-30, 1e-3),
                   clip_threshold=1.0,
                   decay_rate=-0.8,
                   beta1=None,
                   weight_decay=0.0,
                   relative_step=False,
                   scale_parameter=False,
                   warmup_init=False)
