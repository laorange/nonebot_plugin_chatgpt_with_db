import asyncio

import httpx

base_url = "http://127.0.0.1:8090"

test_data1 = {
    "token": 123,
    "qq_id": "",
    "bot_id": ""
}
test_data2 = {
    "qq_id": "test",
    "nick_name": "test",
    "level": 123
}


async def create_record(data):
    async with httpx.AsyncClient() as client:
        await client.post(base_url + "/api/collections/record/records", json=data)


async def creat_qq_account(data):
    async with httpx.AsyncClient() as client:
        _filter = f"?filter=(qq_id='{data['qq_id']}')&perPage=200"
        response = await client.get(base_url + "/api/collections/qq_account/records" + _filter)
        if not len(response.json()['items']):
            await client.post(base_url + "/api/collections/qq_account/records", json=data)


async def get_api_key():
    async with httpx.AsyncClient() as client:
        _filter = f"?perPage=200"
        row_accounts = await client.get(base_url + "/api/collections/bot/records" + _filter)
        records = await client.get(base_url + "/api/collections/record/records" + _filter + "&sort=-created")
        records = list(filter(lambda x: x['id'], records.json()['items']))
        account_set = list(filter(lambda x: x['id'], row_accounts.json()['items']))
        used_time = [records.count(account_set[i - 1]) for i in range(len(account_set))]
        bot_id = row_accounts.json()['items'][used_time.index(min(used_time))]['id']
        api_key = row_accounts.json()['items'][used_time.index(min(used_time))]['key']
        return bot_id, api_key


if __name__ == '__main__':
    asyncio.run(get_api_key())
