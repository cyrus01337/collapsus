"""Explanation"""
import aiosqlite

FILENAME = "quotes.db"
DEFAULT = (
    0,  # uses
)


class InternalQuotesError(Exception):
    def __init__(self, message):
        self.message = message


async def init():
    async with aiosqlite.connect(FILENAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quotes(
                author_id int,
                name varchar(32),
                quote text,
                uses int
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS aliases(
                name varchar(32),
                alias varchar(32)
            );
        """)
        await db.commit()


# helper coroutines
async def owned_by(db, name: str, author_id: int):
    await get("quote", name=name)  # errors if entry doesn't exist
    query = "SELECT * FROM quotes WHERE name=? AND author_id=?;"
    params = (
        name,
        author_id
    )

    async with db.execute(query, params) as cursor:
        quote = await cursor.fetchone()

        if quote is None:
            raise InternalQuotesError("you do not own this quote")
        return True


async def resolve_alias(alias):
    if alias is None:
        return alias
    query = "SELECT name FROM aliases WHERE alias=?;"
    params = (
        alias,
    )

    async with aiosqlite.connect(FILENAME) as db:
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()

            if row is None:
                query = "SELECT name FROM quotes WHERE name=?;"
                alt_cursor = await db.execute(query, params)
                row = await alt_cursor.fetchone()

                if row is None:
                    return row
            return row[0]


# core api
async def add(author_id: id, name: str, quote: str):
    async with aiosqlite.connect(FILENAME) as db:
        try:
            await get("quote", name=name)
        except InternalQuotesError:
            params = (
                author_id,
                name,
                quote,
                *DEFAULT
            )
            values = (", ").join("?" for _ in params)
            query = (f"INSERT INTO quotes (author_id, name, quote, uses) "
                     f"VALUES({values});")

            await db.execute(query, params)
            await db.commit()
        else:
            raise InternalQuotesError("quote already exists")


async def add_alias(name, alias):
    await get("quote", name=name)
    aliases = await resolve_alias(name)

    async with aiosqlite.connect(FILENAME) as db:
        if aliases is not None and alias in aliases:
            raise InternalQuotesError(f'"{alias}" is already an alias for '
                                      f'"{name}"')
        params = (
            name,
            alias
        )

        await db.execute("INSERT INTO aliases VALUES (?,?);", params)
        await db.commit()


async def get(*args, **kwargs):
    get_all = kwargs.pop("all", False)
    db_name = kwargs.pop("db", "quotes")
    fallback = kwargs.pop("fallback", None)
    fallback_params = kwargs.pop("params", tuple())
    conditions = ""

    if args == []:
        args.append("quote")
    if get_all:
        args = "*"
    if kwargs:
        conditions = "WHERE " + (" AND ").join(f"{k}=?" for k in kwargs)
    selecting = (", ").join(args)
    query = f"SELECT {selecting} FROM {db_name} {str.strip(conditions)};"
    params = tuple(kwargs.values())

    async with aiosqlite.connect(FILENAME) as db:
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()

            if row is None and fallback is not None:
                alt_cursor = await db.execute(fallback, fallback_params)
                row = await alt_cursor.fetchone()
            if row is None:
                raise InternalQuotesError("quote doesn't exist")

            if len(row) == 1:
                row = row[0]
            return row


# async def get(name, *args):
#     if args == []:
#         args.append("quote")
#     selecting = (", ").join(args)
#     query = f"SELECT {selecting} FROM quotes WHERE name=?;"
#     params = (
#         name,
#     )

#     async with aiosqlite.connect(FILENAME) as db:
#         async with db.execute(query, params) as cursor:
#             quote = await cursor.fetchone()

#             if quote is None:
#                 original = await resolve_alias(name)
#                 aliases = await get_aliases(original)

#                 if None in [original, aliases]:
#                     raise InternalQuotesError("quote doesn't exist")
#                 params = (
#                     original,
#                 )

#                 alt_cursor = await db.execute(query, params)
#                 quote = await alt_cursor.fetchone()
#             return quote[0]


async def get_aliases(name):
    ret = []
    query = "SELECT alias FROM aliases WHERE name=?;"
    params = (
        name,
    )

    async with aiosqlite.connect(FILENAME) as db:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()

            for row in rows:
                if len(row) == 1:
                    row = row[0]
                ret.append(row)
            return ret or None


async def get_all(author_id, *args):
    args = args or "*"
    selecting = (", ").join(args)
    query = f"SELECT {selecting} FROM quotes WHERE author_id=?;"
    ret = []
    params = (
        author_id,
    )

    async with aiosqlite.connect(FILENAME) as db:
        async with db.execute(query, params) as cursor:
            retrieved = await cursor.fetchall()

            if retrieved is not None:
                for entry in retrieved:
                    if isinstance(entry, tuple) and len(entry) == 1:
                        ret.append(entry[0])

            if len(ret) == 0:
                return None
            return ret


async def increment(author_id, name):
    query = "SELECT uses FROM quotes WHERE name=?;"
    params = (
        name,
    )

    async with aiosqlite.connect(FILENAME) as db:
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            uses = row[0]

            await edit(author_id, name, check=False, uses=uses+1)
            # await db.commit() - edit() commits


async def edit(author_id, name, check: bool = True, **kwargs):
    setting = (", ").join(f"{k}=?" for k in kwargs)
    query = f"UPDATE quotes SET {setting} WHERE name=? AND author_id=?;"
    params = (
        *kwargs.values(),
        name,
        author_id
    )

    async with aiosqlite.connect(FILENAME) as db:
        # errors if entry isn't owned by author
        if check:
            await owned_by(db, name, author_id)
        await db.execute(query, params)
        await db.commit()


async def remove(author_id, name, check=owned_by):
    query = "DELETE FROM quotes WHERE author_id=? AND name=?;"
    params = (
        author_id,
        name
    )

    async with aiosqlite.connect(FILENAME) as db:
        if check is not None:
            await check(db, name, author_id)
        await db.execute(query, params)
        await db.commit()
