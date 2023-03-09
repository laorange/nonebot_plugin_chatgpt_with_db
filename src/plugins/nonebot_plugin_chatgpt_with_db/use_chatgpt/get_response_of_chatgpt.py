import re
from random import random

import openai
from pydantic import ValidationError

from .util_types import ChatAccount, ChatGptResponse, ModelCandidate
from ..config import MAX_TOKENS, OVER_BUFFERING


async def get_response_of_chatgpt(model: ModelCandidate, account: ChatAccount, content: str) -> ChatGptResponse:
    openai.api_key = account.api_key

    temperature = random() + 0.2  # between 0.2 and 1.2

    alphanumeric_length = len(re.findall(r'[a-zA-Z0-9]', content))
    non_alphanumeric_length = len(content) - alphanumeric_length
    real_max_tokens = MAX_TOKENS - alphanumeric_length - non_alphanumeric_length * 2 - OVER_BUFFERING

    if model.startswith("gpt-3.5-turbo"):
        raw_response = await openai.ChatCompletion.acreate(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": content}],  # role: "system", "assistant", "user",
            max_tokens=real_max_tokens)
    elif model.startswith("text-davinci-003"):
        raw_response = await openai.Completion.acreate(model=model, prompt=content, temperature=temperature, max_tokens=real_max_tokens)
    else:
        raise NotImplementedError(f"暂不支持该模型：{model}")

    try:
        return ChatGptResponse(**raw_response)
    except ValidationError as e:
        raise RuntimeError(f"This message didn't pass the pydantic: {raw_response}\n{e}")
