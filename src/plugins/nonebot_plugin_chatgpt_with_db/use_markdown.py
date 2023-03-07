from nonebot import on_regex
from nonebot.internal.adapter import Event
from nonebot.rule import to_me

md_handler = on_regex("[Mm][Dd]", rule=to_me(), priority=8, block=True)


@md_handler.handle()
async def handle_first_receive(e: Event):
    if e.get_plaintext():
        await md_handler.send("https://laorange.gitee.io/md")
