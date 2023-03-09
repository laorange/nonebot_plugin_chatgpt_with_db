import asyncio
import traceback

from typing import Union, Type

from nonebot.internal.matcher import Matcher

from nonebot import on_message
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me
from nonebot.log import logger

from .initialize_accounts import chat_accounts
from ..config import DEBUG, PRICE_PER_TOKEN, DEFAULT_MODEL
from ..models import ChatRecord
from .get_response_of_chatgpt import get_response_of_chatgpt
from .util_types import ChatAccount, ModelCandidate


class ChatGptClient:
    def __init__(self, matcher: Union[Matcher, Type[Matcher]], model: ModelCandidate = "gpt-3.5-turbo-0301"):
        self.chat_accounts = chat_accounts
        self.matcher = matcher
        self.model = model

    async def send(self, msg: str):
        if len(msg) < 2000:
            await self.matcher.send(msg)
        else:
            await self.matcher.send(msg[:1500])
            await asyncio.sleep(1)
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
                response = await get_response_of_chatgpt(DEFAULT_MODEL, account, question_text)
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


basic_handler = on_message(rule=to_me(), priority=9)
chatgpt_client = ChatGptClient(matcher=basic_handler)


@basic_handler.handle()
async def use_chatgpt(e: PrivateMessageEvent):
    if e.get_plaintext() and e.sub_type == "friend":
        await chatgpt_client.handle_event(e)
