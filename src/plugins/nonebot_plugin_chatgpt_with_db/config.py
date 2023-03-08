from pydantic import BaseModel, Extra

from .util_types import ModelCandidate

DEBUG = False
MODEL: ModelCandidate = "gpt-3.5-turbo-0301"

MAX_TOKENS = 4096
PRICE_PER_TOKEN = 0.002 * 6.93 / 1000


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
