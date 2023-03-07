from nonebot import get_driver

from .config import Config
from .models import init_database_sync
from .use_chatgpt import *
from .use_markdown import *
from .use_query_database import *

global_config = get_driver().config
config = Config.parse_obj(global_config)

init_database_sync()
