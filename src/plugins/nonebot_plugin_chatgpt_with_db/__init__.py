from nonebot import get_driver

from .config import Config
from .nonebot_plugin_chatgpt_with_db import *

global_config = get_driver().config
config = Config.parse_obj(global_config)
