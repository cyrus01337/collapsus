import re

import discord
import toml

import database
from base import custom


class Bot(custom.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with open("config.toml", "r") as f:
            config = toml.load(f)

        skip = (r"of", r"\ble?v(el)?\.?")
        pattern = (r"|").join(skip)

        self.unwanted = re.compile(pattern, flags=re.I)
        self.db = database.create(config)

        self.load_base_extensions(exclude=["error_handler.py"])
        self.load_extensions("cogs/")

    async def alias_to(self, name, ctx, *args, **kwargs):
        command = self.get_command(name)

        await command(ctx, *args, **kwargs)

    async def on_message(self, message):
        ctx = await self.get_context(message)

        if ctx.valid and ctx.command.name == "grotto":
            message.content = self.unwanted.sub("", message.content)
        await super().on_message(message)

    async def close(self):
        await self.db.close()
        await super().close()


def main():
    bot = Bot(
        owner_ids={668906205799907348, 263694336040894465},
        allowed_mentions=discord.AllowedMentions.none()
    )
    bot.run()


if __name__ == '__main__':
    main()
