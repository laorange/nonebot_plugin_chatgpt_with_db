import asyncio
import json
import time
from dataclasses import dataclass

import openai


@dataclass
class ChatAccount:
    email: str
    password: str
    api_key: str

    def __post_init__(self):
        self.is_busy = False
        self.question_num = 0

    def __enter__(self):
        self.is_busy = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_busy = False
        self.question_num += 1


async def get_response_of_chatgpt(account: ChatAccount, content: str) -> str:
    with account:
        try:
            print(f"start: {time.ctime()}")
            start_time = time.perf_counter()
            openai.api_key = account.api_key
            # full_response = openai.Completion.create(model="text-davinci-003", prompt=content, temperature=0, max_tokens=4000)
            full_response = await openai.Completion.acreate(model="text-davinci-003", prompt=content, temperature=0, max_tokens=4000)
            print(json.dumps(full_response, ensure_ascii=False))
            response = full_response.choices[0].text
            print(f"end: {time.ctime()}, cost time: {time.perf_counter() - start_time}")
        except Exception as e:
            return f"{e}"
        return response.strip()


if __name__ == '__main__':
    a = ChatAccount(**{"email": "929211182@qq.com", "password": "90519dhnb!", "api_key": "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"})
    asyncio.run(get_response_of_chatgpt(a, "What model does chatgpt 3.5 use?"))
