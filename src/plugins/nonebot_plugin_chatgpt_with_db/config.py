from pydantic import BaseModel, Extra

# 是否为调试模式，不便调用chatgpt接口时调试使用，将不会调用ChatGPT接口
DEBUG = False

# $ → ¥ 汇率
EXCHANGE_RATE = 6.93

# 每个token的价格 (RMB)
PRICE_PER_TOKEN = 0.002 * EXCHANGE_RATE / 1000

# 选用模型的名称
DEFAULT_MODEL = "gpt-3.5-turbo"

# 模型的最大token数
MAX_TOKENS = 4096

# 实际提交的 max_tokens = MAX_TOKENS - (英文字符长度 + 2 * 非英文字符长度 + OVER_BUFFERING)
OVER_BUFFERING = 200


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
