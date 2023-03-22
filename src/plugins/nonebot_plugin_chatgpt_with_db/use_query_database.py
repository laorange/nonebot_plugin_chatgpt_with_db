import datetime

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.rule import to_me
from tortoise.functions import Sum

from .use_chatgpt import TempChatWrapper
from .config import PRICE_PER_TOKEN, PRICE_PER_1K_TOKEN_USD, EXCHANGE_RATE
from .models import ChatRecord

query_db_handler = on_fullmatch('查询', rule=to_me(), priority=8, block=True)


async def get_query_msg_of_qq_id(qq_id: str):
    async def query_data(after: datetime.datetime = None):
        query_filter = ChatRecord.filter(qq=qq_id, created__gt=after) if after else ChatRecord.filter(qq=qq_id)
        query_times = len(await query_filter)
        token_nums: int = (await query_filter.annotate(total_token=Sum("token")).first().values("total_token")).get("total_token", 0)
        token_nums = token_nums if token_nums else 0
        price = round(token_nums * PRICE_PER_TOKEN, 5)
        return query_times, token_nums, price

    today = datetime.datetime.utcnow()
    week_times, week_tokens, week_price = await query_data(after=today - datetime.timedelta(days=7))
    month_times, month_tokens, month_price = await query_data(after=today - datetime.timedelta(days=30))
    total_times, total_tokens, total_price = await query_data(after=None)

    price_per_1k_token = round(PRICE_PER_TOKEN * 1000, 5)

    msg = f"开发者调用ChatGPT官方接口，每1000个token成本为{PRICE_PER_1K_TOKEN_USD} * {EXCHANGE_RATE} = {price_per_1k_token}\n\n"
    msg += "以下是您查询量，可供参考：\n\n"
    msg += f"过去7天: {week_times}次查询，{week_tokens} tokens ( {week_price} )\n\n"
    msg += f"过去30天: {month_times}次查询，{month_tokens} tokens ( {month_price} )\n\n" if week_times != month_times else ""
    msg += f"历史总计: {total_times}次查询，{total_tokens} tokens ( {total_price} )\n\n" if month_times != total_times else ""
    msg += "除此以外，服务器租用和维护也有成本。若本项目对您有所帮助，希望能得到您的理解与支持🥰"

    return msg


@query_db_handler.handle()
async def use_query_database(e: PrivateMessageEvent):
    with TempChatWrapper(query_db_handler, e.sub_type == "group") as matcher:
        await matcher.send(await get_query_msg_of_qq_id(e.get_user_id()))
