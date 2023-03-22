import asyncio
import traceback
from typing import Union, Type

from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.log import logger

from ...models import ChatRecord
from ...config import DEBUG, PRICE_PER_TOKEN, DEFAULT_MODEL
from .initialize_accounts import chat_accounts
from .get_response_of_chatgpt import get_response_of_chatgpt
from .types import ChatAccount, ModelCandidate


class FromFriendHandler:
    def __init__(self, matcher: Union[Matcher, Type[Matcher]], model: ModelCandidate = DEFAULT_MODEL):
        self.chat_accounts = chat_accounts
        self.matcher = matcher
        self.model = model

    async def send(self, user_id: str, msg: str):
        logger.info(f"To {user_id}: {msg}")
        if len(msg) < 2000:
            await self.matcher.send(msg)
        else:
            await self.matcher.send(msg[:1500])
            await asyncio.sleep(1)
            await self.send(user_id, msg[1500:])

    def get_a_chat_account(self) -> ChatAccount:
        return min(self.chat_accounts, key=lambda x: x.used_token)

    async def reject_too_long_question(self, event: PrivateMessageEvent):
        question_text = event.get_plaintext()
        if (question_len := len(question_text)) >= 2000:
            await self.matcher.finish(f"您的问题过长({question_len}个字符)。由于语言模型限制，问题与回答的长度是有上限的，请将问题控制在2000个字符以内")

    async def reply_event(self, event: PrivateMessageEvent):
        question_text = event.get_plaintext()
        user_id = event.get_user_id()
        account = self.get_a_chat_account()

        if DEBUG:  # 用于本地调适 不便调用chatgpt接口时使用
            content = f"you send: {question_text}"
            total_tokens = len(f"{content}{question_text}")

        else:
            response = await get_response_of_chatgpt(self.model, account, question_text)
            content = response.get_content()
            total_tokens = response.usage.total_tokens

        account.used_token += total_tokens

        price = PRICE_PER_TOKEN * total_tokens
        final_response_content = content + f"\n\n> {total_tokens} tokens: {price:.5f} ​元"

        # 将本条消息消耗的token信息存入数据库
        await ChatRecord.create(**{
            "qq": event.sender.user_id,
            "nickname": event.sender.nickname,
            "token": total_tokens,
        })

        await self.send(user_id, final_response_content)

    async def handle_event(self, event: PrivateMessageEvent):
        try:
            await self.reject_too_long_question(event)
            await self.reply_event(event)
        except Exception as e:
            logger.error(traceback.format_exc())
            await self.send(event.get_user_id(), f"{e}")
