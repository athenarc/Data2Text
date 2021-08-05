from yacs.config import CfgNode as CN

# -----------------------------------------------------------------------------
# Convention about Training / Test specific parameters
# -----------------------------------------------------------------------------
# Whenever an argument can be either used for training or for testing, the
# corresponding name will be post-fixed by a _TRAIN for a training parameter,
# or _TEST for a test-specific parameter.
# For example, the number of images during training will be
# IMAGES_PER_BATCH_TRAIN, while the number of images for testing will be
# IMAGES_PER_BATCH_TEST

# -----------------------------------------------------------------------------
# Config definition
# -----------------------------------------------------------------------------

_C = CN()

_C.MODEL = CN()
_C.MODEL.DEVICE = "cuda"
_C.MODEL.GPUS_NUMB = 0
_C.MODEL.MAX_INPUT_TOKENS = 512
_C.MODEL.MAX_OUTPUT_TOKENS = 512
_C.MODEL.TOKENIZER_NAME = "t5-small"
_C.MODEL.PRETRAINED_MODEL_NAME = "t5-small"

# -----------------------------------------------------------------------------
# INPUT
# -----------------------------------------------------------------------------
_C.INPUT = CN()
# Batch size during training
_C.INPUT.SIZE_TRAIN = 4
# Batch size during testing
_C.INPUT.SIZE_TEST = 4

# -----------------------------------------------------------------------------
# Dataset
# -----------------------------------------------------------------------------
_C.DATASET = CN()
# List of the dataset names for training
_C.DATASET.TRAIN = "storage/datasets/totto/filtered/train.json"
# List of the dataset names for validation
_C.DATASET.VALIDATION = "storage/datasets/totto/filtered/dev.json"
# List of the dataset names for testing
_C.DATASET.TEST = ""

# -----------------------------------------------------------------------------
# DataLoader
# -----------------------------------------------------------------------------
_C.DATALOADER = CN()
# Number of data loading threads
_C.DATALOADER.NUM_WORKERS = 6

# ---------------------------------------------------------------------------- #
# Solver
# ---------------------------------------------------------------------------- #
_C.SOLVER = CN()
_C.SOLVER.OPTIMIZER_NAME = "SGD"

_C.SOLVER.MAX_EPOCHS = 50

_C.SOLVER.BASE_LR = 0.001
_C.SOLVER.BIAS_LR_FACTOR = 2

_C.SOLVER.MOMENTUM = 0.9

_C.SOLVER.WEIGHT_DECAY = 0.0005
_C.SOLVER.WEIGHT_DECAY_BIAS = 0

_C.SOLVER.GAMMA = 0.1
_C.SOLVER.STEPS = (30000,)

_C.SOLVER.WARMUP_FACTOR = 1.0 / 3
_C.SOLVER.WARMUP_ITERS = 500
_C.SOLVER.WARMUP_METHOD = "linear"

_C.SOLVER.CHECKPOINT_PERIOD = 1
_C.SOLVER.LOG_PERIOD = 50

# ---------------------------------------------------------------------------- #
# Output paths
# ---------------------------------------------------------------------------- #
_C.OUTPUT = CN()
_C.OUTPUT.LOGGER_DIR = "storage/logs/runtime/"
_C.OUTPUT.MODEL_LOGS_DIR = "storage/logs/model/"
_C.OUTPUT.WANDB_LOGS_DIR = "storage/logs/"
_C.OUTPUT.PLOTS_DIR = "storage/plots/"
_C.OUTPUT.CHECKPOINTS_DIR = "storage/plots/checkpoints"

# ---------------------------------------------------------------------------- #
# Wandb options
# ---------------------------------------------------------------------------- #
_C.WANDB = CN()
_C.WANDB.TAGS = None
_C.WANDB.RUN_NAME = None

# ---------------------------------------------------------------------------- #
# Misc. options
# ---------------------------------------------------------------------------- #
_C.MISC = CN()
_C.MISC.LOGGER_LEVEL = "INFO"
