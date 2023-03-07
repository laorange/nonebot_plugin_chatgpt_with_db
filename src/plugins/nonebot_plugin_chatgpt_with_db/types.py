from typing import List, Literal, Optional

import pydantic

ModelCandidate = Literal["gpt-3.5-turbo", "gpt-3.5-turbo-0301",  "text-davinci-003"]


class TokenUsage(pydantic.BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class GptTurboMessage(pydantic.BaseModel):
    role: str
    content: str


class ResponseChoice(pydantic.BaseModel):
    message: Optional[GptTurboMessage]
    text: Optional[str]
    finish_reason: Optional[Literal["stop", "length", "content_filter"]]
    index: int


class ChatGptResponse(pydantic.BaseModel):
    id: str
    object: str
    created: int
    model: str
    usage: TokenUsage
    choices: List[ResponseChoice]

    def get_content(self):
        choice = self.choices[0]
        if choice.message:
            content = choice.message.content
        elif choice.text:
            content = choice.text
        else:
            content = "您似乎来到了内容的荒原..."
        return content.strip()


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

    text_response2 = {"id": "xxx",
                      "object": "text_completion",
                      "created": 1678200628,
                      "model": "text-davinci-003",
                      "choices": [{
                          "text": "xxx",
                          "index": 0,
                          "logprobs": None,
                          "finish_reason": "stop"
                      }],
                      "usage": {"prompt_tokens": 2, "completion_tokens": 152, "total_tokens": 154}}

    print(ChatGptResponse(**test_response).get_content())
    print(ChatGptResponse(**text_response2).get_content())
