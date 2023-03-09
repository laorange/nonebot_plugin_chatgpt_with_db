import traceback
from typing import Type

from nonebot import logger
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.internal.matcher import Matcher

from .types import LongChatCache
from .from_friend_handler import FromFriendHandler

long_chat_cache: LongChatCache = {}


class TempChatWrapper:
    def __init__(self, matcher: Type[Matcher], ignore_action_failed: bool = True):
        self.matcher = matcher
        self.ignore_action_failed = ignore_action_failed

    def __enter__(self):
        return self.matcher

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not (self.ignore_action_failed and exc_type.__name__ == "ActionFailed"):
            logger.error(traceback.format_exc())
        return True  # 返回值为True，不再传播异常


class FromTempChatHandler(FromFriendHandler):
    async def send(self, user_id: str, msg: str):
        with TempChatWrapper(self.matcher) as matcher:
            logger.info(f"To {user_id}: {msg}")

            if len(msg) < 2000:
                await matcher.send(msg)
            else:
                to_send_msg = msg[:1500]
                to_send_msg += f"\n\n(本回答仍有{len(msg) - 1500}字未发送，请回复任意文本来获取下一段)"

                long_chat_cache[user_id] = msg[1500:]

                await matcher.send(to_send_msg)

    async def handle_event(self, event: PrivateMessageEvent):
        user_id = event.get_user_id()

        if cache := long_chat_cache.get(user_id, None):
            return await self.send(user_id, cache)

        try:
            await self.reject_too_long_question(event)
            await self.reply_event(event)
        except Exception as e:
            logger.error(traceback.format_exc())
            await self.send(user_id, f"{e}")
