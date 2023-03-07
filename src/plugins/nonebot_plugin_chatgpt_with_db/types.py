from typing import List, Literal

import pydantic


class TokenUsage(pydantic.BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class GptTurboMessage(pydantic.BaseModel):
    role: str
    content: str


class ResponseChoice(pydantic.BaseModel):
    message: GptTurboMessage
    finish_reason: Literal["stop", "length", "content_filter", "null"]
    index: int


class ChatGptResponse(pydantic.BaseModel):
    id: str
    object: str
    created: int
    model: str
    usage: TokenUsage
    choices: List[ResponseChoice]


if __name__ == '__main__':
    test_response = {
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": "xxx",
                    "role": "assistant"
                }
            }
        ],
        "created": 1678179225,
        "id": "chat-xxxx",
        "model": "gpt-3.5-turbo-0301",
        "object": "chat.completion",
        "usage": {
            "completion_tokens": 21,
            "prompt_tokens": 11,
            "total_tokens": 32
        }
    }
    print(ChatGptResponse(**test_response))
