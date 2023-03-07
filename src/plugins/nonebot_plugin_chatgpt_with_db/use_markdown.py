from nonebot import on_regex
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me

md_handler = on_regex("[Mm][Dd]", rule=to_me(), priority=8, block=True)


@md_handler.handle()
async def handle_first_receive(e: PrivateMessageEvent):
    if e.get_plaintext():
        await md_handler.send("https://laorange.gitee.io/md")
