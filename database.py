"""Explanation"""
import aiosqlite

FILENAME = "quotes.db"
DEFAULT = (
    0,  # uses
)


class InternalQuotesError(Exception):
    def __init__(self, message):
        self.message = message


class Database(object):
    FILENAME = "quotes.db"
    DEFAULT = (
        0,  # uses
    )

    def __init__(self, connection, loop):
        self._connection = connection

    @classmethod
    async def create(cls, loop):
        connection = await aiosqlite.connect(cls.FILENAME)
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS quotes(
                author_id int,
                name varchar(32),
                quote text,
                uses int
            );
        """)
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS aliases(
                name varchar(32),
                alias varchar(32)
            );
        """)
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS blacklist(
                member_id int
            );
        """)

        await connection.commit()
        return cls(connection, loop)

    # helper coroutines
    async def owned_by(self, name, author_id):
        await self.get("quote", name=name)  # errors if entry doesn't exist
        query = "SELECT * FROM quotes WHERE name=? AND author_id=?;"
        params = (
            name,
            author_id
        )

        async with self._connection.execute(query, params) as cursor:
            quote = await cursor.fetchone()

            if quote is None:
                raise InternalQuotesError("you do not own this quote")
            return True

    async def resolve_alias(self, alias):
        if alias is None:
            return alias
        query = "SELECT name FROM aliases WHERE alias=?;"
        params = (
            alias,
        )

        async with self._connection.execute(query, params) as cursor:
            row = await cursor.fetchone()

            if row is None:
                query = "SELECT name FROM quotes WHERE name=?;"
                alt_cursor = await self._connection.execute(query, params)
                row = await alt_cursor.fetchone()

                if row is None:
                    return row
            return row[0]

    async def in_blacklist(self, member_id, expect=False):
        query = "SELECT member_id FROM blacklist WHERE member_id=?;"
        params = (
            member_id,
        )

        async with self._connection.execute(query, params) as cursor:
            row = await cursor.fetchone()

            if expect is False:
                if row is None:
                    raise InternalQuotesError("member is already blacklisted")
            elif expect is True:
                if row is not None:
                    raise InternalQuotesError("member is already blacklisted")
            return expect

    # core api
    async def add(self, author_id: id, name: str, quote: str):
        try:
            await self.get("quote", name=name)
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

            await self._connection.execute(query, params)
            await self._connection.commit()
        else:
            raise InternalQuotesError("quote already exists")

    async def add_alias(self, name, alias):
        await self.get("quote", name=name)
        aliases = await self.resolve_alias(name)

        if aliases is not None and alias in aliases:
            raise InternalQuotesError(f'"{alias}" is already an alias for '
                                      f'"{name}"')
        query = "INSERT INTO aliases VALUES (?,?);"
        params = (
            name,
            alias
        )

        await self._connection.execute(query, params)
        await self._connection.commit()

    async def get(self, *args, **kwargs):
        get_all = kwargs.pop("all", False)
        db_name = kwargs.pop("self._connection", "quotes")
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

        async with self._connection.execute(query, params) as cursor:
            row = await cursor.fetchone()

            if row is None and fallback is not None:
                args = (fallback, fallback_params)
                alt_cursor = await self._connection.execute(*args)
                row = await alt_cursor.fetchone()
            if row is None:
                raise InternalQuotesError("quote doesn't exist")

            if len(row) == 1:
                row = row[0]
            return row

    async def get_aliases(self, name):
        ret = []
        query = "SELECT alias FROM aliases WHERE name=?;"
        params = (
            name,
        )

        async with self._connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()

            for row in rows:
                if len(row) == 1:
                    row = row[0]
                ret.append(row)
            return ret or None

    async def get_all(self, author_id, *args):
        args = args or "*"
        selecting = (", ").join(args)
        query = f"SELECT {selecting} FROM quotes WHERE author_id=?;"
        ret = []
        params = (
            author_id,
        )

        async with self._connection.execute(query, params) as cursor:
            retrieved = await cursor.fetchall()

            if retrieved is not None:
                for entry in retrieved:
                    if isinstance(entry, tuple) and len(entry) == 1:
                        ret.append(entry[0])

            if len(ret) == 0:
                return None
            return ret

    async def increment(self, author_id, name):
        query = "SELECT uses FROM quotes WHERE name=?;"
        params = (
            name,
        )

        async with self._connection.execute(query, params) as cursor:
            row = await cursor.fetchone()
            uses = row[0]

            await self.edit(author_id, name, check=False, uses=uses+1)
            # await self._connection.commit() - edit() commits

    async def edit(self, author_id, name, check: bool = True, **kwargs):
        setting = (", ").join(f"{k}=?" for k in kwargs)
        query = f"UPDATE quotes SET {setting} WHERE name=? AND author_id=?;"
        params = (
            *kwargs.values(),
            name,
            author_id
        )

        # errors if entry isn't owned by author
        if check:
            await self.owned_by(self._connection, name, author_id)
        await self._connection.execute(query, params)
        await self._connection.commit()

    async def remove(self, author_id, name, check=owned_by):
        query = "DELETE FROM quotes WHERE author_id=? AND name=?;"
        params = (
            author_id,
            name
        )

        if check is not None:
            await check(self._connection, name, author_id)
        await self._connection.execute(query, params)
        await self._connection.commit()

    async def blacklist(self, member_id: int, remove=False):
        await self.in_blacklist(member_id, expect=remove)
        query = "INSERT INTO blacklist VALUES ?;"
        params = (
            member_id,
        )

        if remove:
            query = "DELETE FROM blacklist WHERE member_id=?;"

        await self._connection.execute(query, params)
        await self._connection.commit()

    async def close(self):
        await self._connection.close()
