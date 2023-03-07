from pathlib import Path

from tortoise import fields, Tortoise, run_async
from tortoise.models import Model

sqlite_file = Path(__file__).resolve().parent / "db.sqlite3"


class ChatRecord(Model):
    qq = fields.CharField(max_length=32)
    nickname = fields.CharField(max_length=64)
    token = fields.IntField()
    updated = fields.DatetimeField(auto_now=True)
    created = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nickname}: {self.created}"


async def init_database():
    db_exists = sqlite_file.exists()
    await Tortoise.init(db_url=f'sqlite://{sqlite_file}', modules={'models': [__name__]})
    if not db_exists:
        await Tortoise.generate_schemas()


def init_database_sync():
    run_async(init_database())


if __name__ == '__main__':
    init_database_sync()
