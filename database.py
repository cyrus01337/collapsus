import asyncio
import functools
from collections import OrderedDict
from typing import Dict

import asyncpg
from asyncpg.pool import Pool


class Database:
    __slots__ = ("config", "pool", "loop", "settings")
    VALID_SETTINGS = ("embed",)

    class Settings:
        __slots__ = ("embed", "settings")

        def __init__(self, **attrs):
            self.embed = attrs.pop("embed", False)

            self.settings = OrderedDict(embed=self.embed)

        def __iter__(self):
            return iter(self.settings.items())

        def __repr__(self):
            attrs = (" ").join(f"{k}={v}" for k, v in self)

            return f"<Settings {attrs}>"

        def __getitem__(self, key):
            return self.settings[key]

        def __setitem__(self, key, value):
            self.settings[key] = value

            setattr(self, key, value)

        @property
        def values(self):
            return list(self.settings.values())

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
        self.settings: Dict[int, self.Settings] = None

        self.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        self.settings = {}
        self.pool = await asyncpg.create_pool(**self.config)

        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS collapsus;

                CREATE TABLE IF NOT EXISTS collapsus.settings(
                    id SERIAL PRIMARY KEY UNIQUE,
                    member_id BIGINT UNIQUE NOT NULL,
                    embed BOOLEAN DEFAULT FALSE
                );
            """)

            await self._init_cache(conn)

    def _wrap_params(self, params):
        return [[p] for p in params]

    async def _init_cache(self, conn):
        settings = await conn.fetch("SELECT * FROM collapsus.settings;")

        for _, member_id, embed in settings:
            self.settings[member_id] = self.create_settings(embed=embed)

    def create_settings(self, **kwargs):
        return self.Settings(**kwargs)

    @connect
    async def eval(self, conn, query: str, *args):
        return await conn.fetch(query, *args)

    async def close(self):
        statement = """
            INSERT INTO collapsus.settings (member_id, embed)
            VALUES ($1, $2)
            ON CONFLICT (member_id) DO
            UPDATE SET embed = EXCLUDED.embed;
        """
        values = []

        for key, settings in self.settings.items():
            append = [key, *settings.values]

            values.append(append)

        async with self.pool.acquire() as conn:
            await conn.executemany(statement, values)
        await self.pool.close()


def create(*args, **kwargs):
    return Database(*args, **kwargs)
