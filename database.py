import asyncio
import functools

import asyncpg
from asyncpg.pool import Pool


class Database:
    class Settings:
        VALID = ("embed",)

        def __init__(self, **attrs):
            self.embed = attrs.pop("embed")

            self.values = [self.embed]

        def __repr__(self):
            formatting = "<Settings embed={self.embed}>"

            return formatting.format(self)

    def connect(coro):
        @functools.wraps(coro)
        async def predicate(self, *args, **params):
            await self.wait_until_loaded()

            async with self.pool.acquire() as conn:
                return await coro(self, conn, *args, **params)
        return predicate

    def __init__(self, config):
        self.config = config.get("database", config)

        self.pool: Pool = None
        self.loop = asyncio.get_event_loop()

        self.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        self.members = set()
        self.settings = {}
        self.pool = await asyncpg.create_pool(**self.config)

        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS collapsus;

                CREATE TABLE IF NOT EXISTS collapsus.members(
                    id SERIAL PRIMARY KEY,
                    member_id BIGINT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS collapsus.settings(
                    id SERIAL PRIMARY KEY,
                    member_id BIGINT NOT NULL,
                    embed BOOLEAN DEFAULT FALSE
                );
            """)

            await self._init_cache(conn)

    async def _init_cache(self, conn):
        members = await conn.fetch("SELECT member_id FROM collapsus.members;")
        settings = await conn.fetch("SELECT * FROM collapsus.settings;")

        self.members = set(members)

        for _, member_id, embed in settings:
            self.settings[member_id] = self.Settings(embed=embed)

    @connect
    async def eval(self, conn, query: str, *args):
        return await conn.fetch(query, *args)

    async def close(self):
        keys = list(self.settings.keys())
        statements = {
            "INSERT member_id INTO dq9.members VALUES ($1);": keys,
            "INSERT member_id, embed INTO dq9.settings VALUES ($1, $2);": zip(
                keys,
                [s.values for s in self.settings.values()]
            )
        }

        async with self.pool.acquire() as conn:
            for statement, values in statements.items():
                await conn.executemany(statement, values)
        await self.pool.close()


def create(*args, **kwargs):
    return Database(*args, **kwargs)
