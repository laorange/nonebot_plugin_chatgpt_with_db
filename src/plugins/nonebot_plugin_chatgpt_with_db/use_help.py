from nonebot import on_regex
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me

from .use_chatgpt.utils import TempChatWrapper

menu_matcher = on_regex("^([Mm][Ee][Nn][Uu]|菜单|帮助|说明|[Hh]elp|HELP)$", rule=to_me(), priority=8, block=True)

message = '1. 发送"帮助"或"说明"可以查看使用说明\n\n'
message += '2. 发送"查询"可以获取历史使用情况\n\n'
message += '3. 机器人会以markdown格式(简称md)回复代码问题，若您不熟悉md语法，可发送"md"来获取在线解析工具\n\n'
message += '4. 默认消息直接由ChatGPT回复，每1000 tokens为$0.002\n\n'
message += '5. 关于token，例如"ChatGPT is great!" 会被拆为6个token：["Chat", "G", "PT", " is", " great", "!"]'


@menu_matcher.handle()
async def use_help(e: PrivateMessageEvent):
    if e.get_plaintext():
        with TempChatWrapper(menu_matcher, e.sub_type == "group") as matcher:
            await matcher.finish(message)
