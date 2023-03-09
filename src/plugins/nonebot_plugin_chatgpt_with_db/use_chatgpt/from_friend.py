from nonebot import on_message
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me

from .utils import FromFriendHandler

basic_matcher = on_message(rule=to_me(), priority=9)
from_friend_handler = FromFriendHandler(matcher=basic_matcher)


@basic_matcher.handle()
async def from_friend(e: PrivateMessageEvent):
    if e.get_plaintext() and e.sub_type == "friend":
        await from_friend_handler.handle_event(e)
