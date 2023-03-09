from nonebot import on_message
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me

from src.plugins.nonebot_plugin_chatgpt_with_db.use_chatgpt.utils.from_temp_chat_handler import FromTempChatHandler

basic_matcher = on_message(rule=to_me(), priority=9)
from_temp_chat_handler = FromTempChatHandler(matcher=basic_matcher)


@basic_matcher.handle()
async def from_temp_chat(e: PrivateMessageEvent):
    if e.get_plaintext() and e.sub_type == "group":
        await from_temp_chat_handler.handle_event(e)
