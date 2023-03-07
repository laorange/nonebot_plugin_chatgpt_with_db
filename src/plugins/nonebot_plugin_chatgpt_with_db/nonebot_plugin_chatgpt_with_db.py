import asyncio
import json
import time
from dataclasses import dataclass
from typing import List, Union, Type, Literal

from nonebot.internal.matcher import Matcher
import openai

from nonebot import on_message
from nonebot.internal.adapter import Event
from nonebot.rule import to_me
from loguru import logger

from .dbapi import get_api_key, create_record
from .secret import accounts


@dataclass
class EventWrapper:
    event: Event
    status: Literal["waiting", "pending"]

    def __eq__(self, other):
        return self.status == other.status \
            and self.event.get_plaintext() == other.event.get_plaintext() \
            and self.event.get_user_id() == other.event.get_user_id()

    @property
    def is_waiting(self):
        return self.status == "waiting"

    @property
    def is_pending(self):
        return self.status == "pending"

    @property
    def user_id(self):
        return self.event.get_user_id()


@dataclass
class ChatAccount:
    email: str
    password: str
    api_key: str

    def __post_init__(self):
        self.is_busy = False
        self.question_num = 0

    def __enter__(self):
        self.is_busy = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_busy = False
        self.question_num += 1


class ChatGptHandler:
    queue: List[EventWrapper] = []
    chat_accounts: List[ChatAccount] = []

    def __init__(self, matcher: Union[Matcher, Type[Matcher]]):
        self.chat_accounts = [ChatAccount(**account) for account in accounts]
        self.matcher = matcher

    async def send(self, msg: str):
        await self.matcher.send(msg)

    async def finish_with(self, msg: str):
        await self.matcher.finish(msg)

    def get_a_free_account(self) -> Union[ChatAccount, None]:
        if len(free_account := list(filter(lambda a: not a.is_busy, self.chat_accounts))) == 0:
            return None
        return min(free_account, key=lambda x: x.question_num)

    @logger.catch(reraise=True)
    async def reply(self, ew: EventWrapper, q_index: int = -1):
        # 获取空闲账号，若无，则1秒后递归
        account = self.get_a_free_account()
        if account is None:
            await asyncio.sleep(1)
            return await self.reply(ew, q_index=self.queue.index(ew))

        # 若当前 ew 尚未在等待队列的首位，则1秒后递归
        waiting_queue = [eew for eew in self.queue if eew.is_waiting]
        if waiting_queue[0] != ew:
            if q_index != waiting_queue.index(ew):
                await self.send(f"当前队列还有{waiting_queue.index(ew)}个")
            await asyncio.sleep(1)
            return await self.reply(ew, q_index=self.queue.index(ew))

        # 能走到这步，说明 1. 有空闲账号 2. 在等待队列的首位
        await self.send(f"已开始处理您的信息，请耐心等待")
        ew.status = "pending"

        try:
            response = await self.get_response_of_chatgpt(account, ew.event.get_plaintext())
            await self.send(response)
        except Exception as e:
            await self.send(f"{e}")
        finally:
            self.queue = [eew for eew in self.queue if ew != eew]

    @staticmethod
    async def get_response_of_chatgpt(account: ChatAccount, content: str) -> str:
        with account:
            try:
                print(f"start: {time.ctime()}")
                start_time = time.perf_counter()
                bot_id, api_key = await get_api_key()
                openai.api_key = api_key
                print(api_key)
                # full_response = openai.Completion.create(model="text-davinci-003", prompt=content, temperature=0, max_tokens=4000)
                full_response = openai.Completion.acreate(model="text-davinci-003", prompt=content, temperature=0, max_tokens=4000)
                print(json.dumps(full_response, ensure_ascii=False))
                response = full_response.choices[0].text
                print(f"end: {time.ctime()}, cost time: {time.perf_counter() - start_time}")
                # record = {
                #     "token": 123,
                #     "qq_id": "",
                #     "bot_id": ""
                # }
                # await create_record(record)
            except Exception as e:
                return f"出错，{e}"
            return response.strip()


msg_handler = on_message(rule=to_me(), priority=5)
chatgpt_handler = ChatGptHandler(matcher=msg_handler)


@logger.catch(reraise=False)
@msg_handler.handle()
async def handle_first_receive(e: Event):
    print(f"{e.get_plaintext()=}")
    if e.get_plaintext():
        ew = EventWrapper(event=e, status="waiting")

        # 若该用户没有在队列的消息，则添加入队列
        if len([eew for eew in chatgpt_handler.queue if ew.user_id == eew.user_id]) == 0:
            chatgpt_handler.queue.append(ew)
        else:
            return await msg_handler.send("当前您已有消息在队列中，请耐心等待")

        await chatgpt_handler.reply(ew)


# if __name__ == '__main__':
#     import os
#     from pathlib import Path
#     import sys
#
#     os.environ["HOME"] = str(Path(sys.argv[0]).parent)
#
#     handler = ChatGptHandler(matcher=msg_handler)
#     promise = handler.get_response_of_chatgpt(handler.chat_accounts[0], "帮我写一个基于vue3的重置密码页面")
#     asyncio.run(promise)
