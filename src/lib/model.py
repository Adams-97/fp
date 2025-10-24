from abc import ABC

from src.lib.conf import ModelConfig


class Model(ABC):
    def __init__(self):
        self._conf: ModelConfig
