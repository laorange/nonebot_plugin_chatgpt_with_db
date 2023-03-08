import traceback
from pathlib import Path
from random import random
from typing import Union, Type, List

from nonebot.internal.matcher import Matcher
import openai

from nonebot import on_message
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me
from nonebot.log import logger
from pydantic import ValidationError

from .config import DEBUG, PRICE_PER_TOKEN, MAX_TOKENS, MODEL
from .models import ChatRecord
from .util_types import ChatGptResponse


class ChatAccount:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.used_token = 0


def initialize_accounts() -> List[ChatAccount]:
    api_keys_txt = Path(__file__).parent.resolve() / "api-keys.txt"
    if api_keys_txt.exists():
        with api_keys_txt.open("rt", encoding="utf-8") as akt:
            accounts = [ChatAccount(api_key) for api_key in akt.readlines()]
            logger.info(f"当前有{len(accounts)}个账号；若需修改，请编辑或删除: {api_keys_txt}")
            return accounts
    else:
        api_keys = [input("请输入api key: ")]

        while new_api_key := input(f"当前有{len(api_keys)}个账号，若已完成输入请直接回车，或请继续输入下一个api key: "):
            if new_api_key:
                api_keys.append(new_api_key)

        with api_keys_txt.open("wt", encoding="utf-8") as akt:
            akt.write("\n".join(api_keys))

        return [ChatAccount(api_key) for api_key in api_keys if api_key]


class ChatGptHandler:
    def __init__(self, matcher: Union[Matcher, Type[Matcher]]):
        self.chat_accounts = initialize_accounts()
        self.matcher = matcher

    async def send(self, msg: str):
        if len(msg) < 2000:
            await self.matcher.send(msg)
        else:
            await self.matcher.send(msg[:1500])
            await self.send(msg[1500:])

    def get_a_chat_account(self) -> ChatAccount:
        return min(self.chat_accounts, key=lambda x: x.used_token)

    async def handle_event(self, event: PrivateMessageEvent):
        question_text = event.get_plaintext()
        if (question_len := len(question_text)) >= 2000:
            return await self.send(f"您的问题过长({question_len}个字符)。由于语言模型限制，问题与回答的长度是有上限的，请将问题控制在2000个字符以内")

        try:
            await self.send("已收到您的消息，请稍候...")
            account = self.get_a_chat_account()

            if DEBUG:  # 用于本地调适 不便调用chatgpt接口时使用
                content = f"you send: {question_text}"
                total_tokens = len(f"{content}{question_text}")

            else:
                response = await self.get_response_of_chatgpt(account, question_text)
                content = response.get_content()
                total_tokens = response.usage.total_tokens

            account.used_token += total_tokens
            price = PRICE_PER_TOKEN * total_tokens
            final_response_content = content + f"\n\n> {total_tokens} tokens: ¥{price:.5f}"

            # 将本条消息消耗的token信息存入数据库
            await ChatRecord.create(**{
                "qq": event.sender.user_id,
                "nickname": event.sender.nickname,
                "token": total_tokens,
            })

            logger.info(f"To {event.sender.user_id}: {final_response_content}")
            await self.send(final_response_content)
        except Exception as e:
            logger.error(traceback.format_exc())
            await self.send(f"{e}")

    @staticmethod
    async def get_response_of_chatgpt(account: ChatAccount, content: str) -> ChatGptResponse:
        openai.api_key = account.api_key

        temperature = random() + 0.2  # between 0.2 and 1.2

        left_max_tokens = MAX_TOKENS - len(content) * 1.5

        if MODEL.startswith("gpt-3.5-turbo"):
            raw_response = await openai.ChatCompletion.acreate(
                model=MODEL,
                temperature=temperature,
                messages=[{"role": "user", "content": content}],  # role: "system", "assistant", "user",
                max_tokens=left_max_tokens)
        else:  # text-davinci-003
            raw_response = await openai.Completion.acreate(model="text-davinci-003", prompt=content, temperature=temperature, max_tokens=left_max_tokens)

        try:
            return ChatGptResponse(**raw_response)
        except ValidationError as e:
            raise RuntimeError(f"This message didn't pass the pydantic: {raw_response}\n{e}")


basic_handler = on_message(rule=to_me(), priority=9)
chatgpt_handler = ChatGptHandler(matcher=basic_handler)


@basic_handler.handle()
async def use_chatgpt(e: PrivateMessageEvent):
    if e.get_plaintext():
        await chatgpt_handler.handle_event(e)
