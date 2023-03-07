from nonebot import on_request
from nonebot.adapters import Event
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import FriendRequestEvent

add_handler = on_request()


@add_handler.handle()
async def _(bot: Bot, event: Event):
    if isinstance(event, FriendRequestEvent):
        print(f"好友申请: {event.user_id}")
        await bot.call_api("set_friend_add_request", flag=event.flag, remark=event.comment)
