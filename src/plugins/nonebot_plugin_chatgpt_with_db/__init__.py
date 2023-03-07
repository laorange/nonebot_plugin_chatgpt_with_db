from nonebot import get_driver

from .config import Config
from .use_chatgpt import *

global_config = get_driver().config
config = Config.parse_obj(global_config)
