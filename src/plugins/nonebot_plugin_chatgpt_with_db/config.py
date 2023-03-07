from pydantic import BaseModel, Extra

DEBUG = False
MAX_TOKENS = 4000
PRICE_PER_TOKEN = 0.002 * 6.93 / 1000


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
