import traceback
from typing import Type

from nonebot import logger
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.exception import FinishedException
from nonebot.internal.matcher import Matcher

from .types import LongChatCache
from .from_friend_handler import FromFriendHandler


class TempChatWrapper:
    def __init__(self, matcher: Type[Matcher], ignore_action_failed: bool = True):
        self.matcher = matcher
        self.ignore_action_failed = ignore_action_failed

    def __enter__(self):
        return self.matcher

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:  # 没有异常 直接返回
            return False

        if exc_type == FinishedException:  # nonebot 正常流程中的 FinishedException 应直接正常抛出
            return False

        if self.ignore_action_failed and exc_type.__name__ == "ActionFailed":  # 忽略ActionFailed
            return True

        return False  # 其余情况 继续向上抛出异常


class FromTempChatHandler(FromFriendHandler):
    long_chat_cache: LongChatCache = {}

    async def reject_too_long_question(self, event: PrivateMessageEvent):
        with TempChatWrapper(self.matcher):
            await super().reject_too_long_question(event)

    async def send(self, user_id: str, msg: str):
        with TempChatWrapper(self.matcher) as matcher:
            logger.info(f"To {user_id}: {msg}")

            if len(msg) < 2000:
                self.long_chat_cache[user_id] = ""
                await matcher.send(msg)
            else:
                to_send_msg = msg[:1500]
                to_send_msg += f"\n\n(本回答仍有{len(msg) - 1500}字未发送，请回复任意文本来获取下一段)"

                self.long_chat_cache[user_id] = msg[1500:]

                await matcher.send(to_send_msg)

    async def handle_event(self, event: PrivateMessageEvent):
        user_id = event.get_user_id()

        if cache := self.long_chat_cache.get(user_id, None):
            return await self.send(user_id, cache)

        try:
            await self.reject_too_long_question(event)
            await self.reply_event(event)
        except Exception as e:
            logger.error(traceback.format_exc())
            await self.send(user_id, f"{e}")
