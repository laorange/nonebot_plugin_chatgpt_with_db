from nonebot import on_regex
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me

menu_matcher = on_regex("^([Mm][Ee][Nn][Uu]|菜单|帮助|[Hh]elp|HELP)$", rule=to_me(), priority=8, block=True)

message = '1. 发送"帮助"或"菜单"可以查看使用说明\n\n'
message += '2. 发送"查询"可以获取历史使用情况\n\n'
message += '3. 发送"md"可以在线查看markdown文档\n\n'
message += '4. 默认消息直接由ChatGPT回复，价格为1k tokens/$0.002 (1000tokens大约是750个单词)'


@menu_matcher.handle()
async def _(e: PrivateMessageEvent):
    if e.get_plaintext():
        await menu_matcher.finish(message)
