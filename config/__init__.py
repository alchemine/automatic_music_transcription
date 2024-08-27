"""Configuration constants for the project."""

import yaml
from os import environ
from easydict import EasyDict


def load_yaml(path: str) -> EasyDict:
    """Load yaml file."""
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return EasyDict(config)


##################################################
# Configurations
##################################################
CFG_SERVICE = load_yaml("config/service.yaml")
CFG_ENGINE = load_yaml("config/engine.yaml")

ENV = environ["ENV"]
DEBUG = False


if __name__ == "__main__":
    print(ENV)
    print(CFG_SERVICE)
    print(CFG_ENGINE)
