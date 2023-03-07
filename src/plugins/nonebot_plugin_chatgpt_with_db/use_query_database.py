import datetime

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me
from tortoise.functions import Sum

from .config import PRICE_PER_TOKEN
from .models import ChatRecord

query_db_handler = on_fullmatch('查询', rule=to_me(), priority=8, block=True)


async def get_query_msg_of_qq_id(qq_id: str):
    today = datetime.datetime.utcnow()
    a_week_ago = today - datetime.timedelta(days=7)
    a_month_ago = today - datetime.timedelta(days=30)

    times_within_a_week = len(await ChatRecord.filter(qq=qq_id, created__gt=a_week_ago))
    token_within_a_week: int = (await ChatRecord.filter(qq=qq_id, created__gt=a_week_ago).annotate(total_token=Sum("token")).first().values("total_token")).get("total_token", 0)
    token_within_a_week = token_within_a_week if token_within_a_week else 0

    times_within_a_month = len(await ChatRecord.filter(qq=qq_id, created__gt=a_month_ago))
    token_within_a_month: int = (await ChatRecord.filter(qq=qq_id, created__gt=a_month_ago).annotate(total_token=Sum("token")).first().values("total_token")).get("total_token", 0)
    token_within_a_month = token_within_a_month if token_within_a_month else 0

    total_times = len(await ChatRecord.filter(qq=qq_id))
    total_token: int = (await ChatRecord.filter(qq=qq_id).annotate(total_token=Sum("token")).first().values("total_token")).get("total_token", 0)
    total_token = total_token if total_token else 0

    msg = f"程序调用ChatGPT官方接口是付费的，每1000个token成本价为{round(PRICE_PER_TOKEN * 1000, 5)}。\n\n"
    msg += "以下是您查询量，可供参考：\n\n"
    msg += f"过去7天: {times_within_a_week}次查询，{token_within_a_week} tokens (¥{round(token_within_a_week * PRICE_PER_TOKEN, 5)})\n\n"
    msg += f"过去30天: {times_within_a_month}次查询，{token_within_a_month} tokens (¥{round(token_within_a_month * PRICE_PER_TOKEN, 5)})\n\n"
    msg += f"历史总计: {total_times}次查询，{total_token} tokens (¥{round(total_token * PRICE_PER_TOKEN, 5)})\n\n"
    msg += "🥰希望能得到您的理解与支持"

    return msg


@query_db_handler.handle()
async def use_query_database(e: PrivateMessageEvent):
    await query_db_handler.send(await get_query_msg_of_qq_id(e.get_user_id()))
