"""Generic file handling functions."""

from glob import glob
from os.path import isfile, isdir

import yaml
from easydict import EasyDict


############################################################
# Lambda functions
############################################################
ls_all = lambda path: [path for path in glob(f"{path}/*")]
ls_dir = lambda path: [path for path in glob(f"{path}/*") if isdir(path)]
ls_file = lambda path: [path for path in glob(f"{path}/*") if isfile(path)]


############################################################
# File loading functions
############################################################
def load_yaml(path: str) -> EasyDict:
    """Load yaml file."""
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return EasyDict(config)
