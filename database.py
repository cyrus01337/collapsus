import asyncio
import functools
from collections import OrderedDict
from typing import Coroutine, Dict

import asyncpg
from asyncpg.pool import Pool


class Database:
    __slots__ = ("config", "loop", "ready_event", "pool", "settings")
    VALID_SETTINGS = ("embed",)

    class DottedRecord(asyncpg.Record):
        __getattr__ = asyncpg.Record.__getitem__

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
            await self.wait_until_ready()

            async with self.pool.acquire() as conn:
                return await coro(self, conn, *args, **params)
        return predicate

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.ready_event = asyncio.Event()
        self.pool: Pool = None
        self.settings: Dict[int, self.Settings] = {}

        self.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        self.pool = await asyncpg.create_pool(
            user="cyrus",
            password="root",
            database="bots",
            record_class=self.DottedRecord
        )

        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS collapsus;

                CREATE TABLE IF NOT EXISTS collapsus.settings(
                    id SERIAL PRIMARY KEY UNIQUE,
                    member_id BIGINT UNIQUE NOT NULL,
                    embed BOOLEAN DEFAULT FALSE
                );

                CREATE TABLE IF NOT EXISTS collapsus.quotes(
                    name TEXT PRIMARY KEY UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    author_id BIGINT NOT NULL
                );
            """)

            await self._init_cache(conn)

    async def _init_cache(self, conn):
        settings = await conn.fetch("SELECT * FROM collapsus.settings;")

        for _, member_id, embed in settings:
            self.settings[member_id] = self.create_settings(embed=embed)
        self.ready_event.set()

    def _create_condition(self, attrs):
        return " AND ".join(
            f"{key} = ${i}"
            for i, (key, value) in enumerate(attrs.items(), start=1)
        )

    def _wrap_params(self, params):
        return [[p] for p in params]

    async def wait_until_ready(self):
        return await self.ready_event.wait()

    def create_settings(self, **kwargs):
        return self.Settings(**kwargs)

    @connect
    async def get_quote(self, conn, **attrs):
        condition = self._create_condition(attrs)
        query = f"SELECT * FROM collapsus.quotes WHERE {condition};"

        return await conn.fetchrow(query, *attrs.values())

    @connect
    async def get_all_quotes(self, conn, author_id):
        query = "SELECT * FROM collapsus.quotes WHERE author_id=$1;"

        return await conn.fetch(query, author_id)

    @connect
    async def add_quote(self, conn, name, content, author_id):
        query = """
            INSERT INTO collapsus.quotes(name, content, author_id)
            VALUES($1, $2, $3)
            ON CONFLICT (name) DO NOTHING;
        """

        await conn.execute(query, name, content, author_id)

    @connect
    async def owns_quote(self, conn, author_id, name):
        query = """
            SELECT * FROM collapsus.quotes WHERE author_id=$1 AND name=$2;
        """
        quote = await conn.fetch(query, author_id, name)

        return bool(quote)

    @connect
    async def update_quote(self, conn, name, content):
        query = "UPDATE collapsus.quotes SET content=$2 WHERE name=$1;"

        await conn.execute(query, name, content)

    @connect
    async def remove_quote(self, conn, name):
        await conn.execute("DELETE FROM collapsus.quotes WHERE name=$1;", name)

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
