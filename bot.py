import json
import pathlib
import re

import discord
from discord.ext import commands

import database

CONFIG = {}

with open("config.json") as fh:
    CONFIG = json.load(fh)


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        CWD = pathlib.Path.cwd()
        skip = (r"of", r"\ble?v(el)?\.?")
        pattern = (r"|").join(skip)

        self.started = False
        self.unwanted = re.compile(pattern, flags=re.I)
        self.db = database.create()

        for obj in CWD.glob("./cogs/*.py"):
            self.load_extension(f"cogs.{obj.stem}")

    async def alias_to(self, name, ctx, *args, **kwargs):
        command = self.get_command(name)

        await command(ctx, *args, **kwargs)

    async def on_message(self, message):
        ctx = await self.get_context(message)

        if ctx.valid and ctx.command.name == "grotto":
            message.content = self.unwanted.sub("", message.content)
        await super().on_message(message)

    async def on_ready(self):
        if self.started:
            return
        self.started = True

        print(self.user.name, end="\n\n")

    def run(self):
        super().run(CONFIG["token"])

    async def close(self):
        await self.db.close()
        await super().close()


def main():
    bot = Bot(
        allowed_mentions=discord.AllowedMentions.none(),
        command_prefix=commands.when_mentioned_or(".t"),
        owner_ids={668906205799907348, 263694336040894465}
    )

    bot.run()


if __name__ == '__main__':
    main()
