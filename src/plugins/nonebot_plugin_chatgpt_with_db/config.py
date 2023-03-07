from pydantic import BaseModel, Extra

from .types import ModelCandidate

DEBUG = False
MODEL: ModelCandidate = "text-davinci-003"

MAX_TOKENS = 4000
PRICE_PER_TOKEN = 0.002 * 6.93 / 1000


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
