import re

import discord

from base import custom


class Bot(custom.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unwanted = re.compile("of", flags=re.I)

        self.load_base_extensions(exclude=["error_handler.py"])
        self.load_extensions("cogs/")

    async def on_message(self, message):
        unwanted_found = self.unwanted.search(message.content)
        ctx = await self.get_context(message)

        if unwanted_found and ctx.valid and ctx.command.name == "grotto":
            message.content = self.unwanted.sub("", message.content)
        await super().on_message(message)


def main():
    bot = Bot(
        owner_ids={668906205799907348, 263694336040894465},
        allowed_mentions=discord.AllowedMentions.none()
    )
    bot.run()


if __name__ == '__main__':
    main()
