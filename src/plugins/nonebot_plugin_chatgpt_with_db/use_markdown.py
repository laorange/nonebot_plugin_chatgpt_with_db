from nonebot import on_regex
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me

from .use_chatgpt import TempChatWrapper

md_handler = on_regex("^[Mm][Dd]$", rule=to_me(), priority=8, block=True)


@md_handler.handle()
async def use_markdown(e: PrivateMessageEvent):
    if e.get_plaintext():
        with TempChatWrapper(md_handler, e.sub_type == "group") as matcher:
            await matcher.send("https://laorange.gitee.io/md")
