from pydantic import BaseModel, Extra

DEBUG = False

MAX_TOKENS = 4096
PRICE_PER_TOKEN = 0.002 * 6.93 / 1000
DEFAULT_MODEL = "gpt-3.5-turbo-0301"


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
