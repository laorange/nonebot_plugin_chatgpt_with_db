from pathlib import Path
from typing import List

from nonebot import logger

from .types import ChatAccount


def initialize_accounts() -> List[ChatAccount]:
    api_keys_txt = Path(__file__).parent.resolve() / "api-keys.txt"
    if api_keys_txt.exists():
        with api_keys_txt.open("rt", encoding="utf-8") as akt:
            accounts = [ChatAccount(api_key) for api_key in akt.readlines()]
            logger.info(f"当前有{len(accounts)}个账号；若需修改，请编辑或删除: {api_keys_txt}")
            return accounts
    else:
        api_keys = [input("请输入api key: ")]

        while new_api_key := input(f"当前有{len(api_keys)}个账号，若已完成输入请直接回车，或请继续输入下一个api key: "):
            if new_api_key:
                api_keys.append(new_api_key)

        with api_keys_txt.open("wt", encoding="utf-8") as akt:
            akt.write("\n".join(api_keys))

        return [ChatAccount(api_key) for api_key in api_keys if api_key]


chat_accounts = initialize_accounts()
