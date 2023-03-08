from nonebot import on_regex
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me

menu_matcher = on_regex("^([Mm][Ee][Nn][Uu]|菜单|帮助|说明|[Hh]elp|HELP)$", rule=to_me(), priority=8, block=True)

message = '1. 发送"帮助"或"说明"可以查看使用说明\n\n'
message += '2. 发送"查询"可以获取历史使用情况\n\n'
message += '3. 机器人会以markdown格式(简称md)回复代码问题，若您不熟悉md语法，可发送"md"来获取在线解析工具\n\n'
message += '4. 默认消息直接由ChatGPT回复，价格为1k tokens/$0.002 (大约为7.2w词/1元)'


@menu_matcher.handle()
async def _(e: PrivateMessageEvent):
    if e.get_plaintext():
        await menu_matcher.finish(message)
