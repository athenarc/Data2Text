from yacs.config import CfgNode as CN

# -----------------------------------------------------------------------------
# Backend Config
# -----------------------------------------------------------------------------

_C = CN()

_C.MODEL = CN()
_C.MODEL.DEVICE = "cpu"
_C.MODEL.GPUS_NUMB = 1
_C.MODEL.MAX_INPUT_TOKENS = 512
_C.MODEL.MAX_OUTPUT_TOKENS = 64
_C.MODEL.TOKENIZER_NAME = "t5-small"
_C.MODEL.PRETRAINED_MODEL_NAME = "t5-small"
_C.MODEL.PATH_TO_CHECKPOINT = "storage/checkpoints/full_entities/t5_small/epoch=3-step=60579.ckpt"

# -----------------------------------------------------------------------------
# FastAPI
# -----------------------------------------------------------------------------
_C.FASTAPI = CN()
# Batch size during training
_C.FASTAPI.WORKERS = 1
_C.FASTAPI.DEBUG = True
_C.FASTAPI.RELOAD = True
_C.FASTAPI.HOST = '0.0.0.0'
_C.FASTAPI.PORT = 4557

# ---------------------------------------------------------------------------- #
# Database Info
# ---------------------------------------------------------------------------- #
_C.DB = CN()
_C.DB.PATH = ""

# ---------------------------------------------------------------------------- #
# Solver
# ---------------------------------------------------------------------------- #
_C.SOLVER = CN()
_C.SOLVER.OPTIMIZER_NAME = "Adam"  # Possible values Adam, AdaFactor (case sensitive)
_C.SOLVER.MAX_EPOCHS = 50
_C.SOLVER.BASE_LR = 0.001
_C.SOLVER.CHECKPOINT_PERIOD = 1
_C.SOLVER.LOG_PERIOD = 50

# ---------------------------------------------------------------------------- #
# Misc. options
# ---------------------------------------------------------------------------- #
_C.MISC = CN()
_C.MISC.LOGGER_LEVEL = "INFO"
