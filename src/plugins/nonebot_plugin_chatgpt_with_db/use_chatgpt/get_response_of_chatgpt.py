from random import random

import openai
from pydantic import ValidationError

from .util_types import ChatAccount, ChatGptResponse, ModelCandidate
from ..config import MAX_TOKENS


async def get_response_of_chatgpt(model: ModelCandidate, account: ChatAccount, content: str) -> ChatGptResponse:
    openai.api_key = account.api_key

    temperature = random() + 0.2  # between 0.2 and 1.2

    left_max_tokens = int(MAX_TOKENS - len(content) * 1.5)

    if model.startswith("gpt-3.5-turbo"):
        raw_response = await openai.ChatCompletion.acreate(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": content}],  # role: "system", "assistant", "user",
            max_tokens=left_max_tokens)
    else:  # text-davinci-003
        raw_response = await openai.Completion.acreate(model="text-davinci-003", prompt=content, temperature=temperature, max_tokens=left_max_tokens)

    try:
        return ChatGptResponse(**raw_response)
    except ValidationError as e:
        raise RuntimeError(f"This message didn't pass the pydantic: {raw_response}\n{e}")
