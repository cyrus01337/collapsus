"""Discord bot base"""
import asyncio
import os

import discord
from discord.ext import commands

import _token
import emojis
import prefix
import utils
from constants import Owner
from constants import Status


class GrottoBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(case_insensitive=True, reconnect=True,
                         **prefix.as_kwarg())
        self.owner_ids = Owner.all()

        self.is_online = False
        self.received_love = False
        self.invite = None
        self.channel = None
        # wow this looks like json
        self.reminders = {
            "todo": {
                "run": (
                    "add editable prefix settings"
                ),
            },
            "idea": {
                "custom": (
                    "create custom.py and create own Embed class",
                    ("re-design self.reminders into it's own object "
                     "(place into owner.py upon completion)"),
                ),
                "owner": (
                    ("create owner-specific cog for live eval/exec "
                     "functionality"),
                    ("setup reminders to be dynamic instead of a static "
                     "variable sitting in a file"),
                    "owner-only reminders command :^)",
                ),
                "settings": (
                    ("have to leave your configuration files locked up "
                     "somewhere"),
                ),
                "dq9": (
                    ("include hyperlink formatting with "
                     "http://example.com/ as the URL to mimic detail format "
                     "on Yab's site"),
                    "create grotto object to make formatting easier",
                    ("find method of storing aiohttp.ClientSession instance "
                     "for repeated usage if available")
                )
            }
        }
        self.invite_perms = discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            embed_links=True
        )

        for file in self.get_cog_filenames():
            self.load_extension(f"cogs.{file}")

        self.loop.create_task(self.setup())
        self.loop.create_task(self.init_display())

    # tasks
    async def setup(self):
        await self.wait_until_ready()
        self.channel = await self.fetch_channel(692867688325709835)
        self.invite = discord.utils.oauth_url(
            client_id=self.user.id,
            permissions=discord.Permissions(
                send_messages=True,
                read_messages=True,
                read_message_history=True,
                manage_messages=True,
                add_reactions=True,
                embed_links=True
            )
        )

        await self.alert(status=Status.UP)

    async def init_display(self):
        await self.wait_until_ready()
        activity = discord.Activity(type=discord.ActivityType.listening,
                                    name=f"{prefix.DEFAULT} and pings!")

        utils.clear_screen()
        print(self.user.name, end="\n\n")
        await self.change_presence(activity=activity)

    # helper methods
    def get_cog_filenames(self):
        ret = []

        for name in os.listdir("./cogs"):
            if name.endswith(".py"):
                ret.append(name[:-3])
        return ret

    async def alert(self, status: Status):
        message = f"I'm {str.lower(status.name)}"

        for owner_id in self.owner_ids:
            owner = self.get_user(owner_id)

            try:
                await owner.send(f"{message} Dad")
            except discord.Forbidden:
                continue
        try:
            await self.channel.send(message)
        except discord.Forbidden:
            return

    async def send_embed(self, ctx, message=None, *args, **kwargs):
        args = [message]
        title = kwargs.pop("title", None)
        description = utils.multi_pop(kwargs, "description", "desc")
        fields = kwargs.pop("fields", {})
        footer = kwargs.pop("footer", None)
        image = kwargs.pop("image", None)
        embed = discord.Embed(title=title, description=description)

        for name, value in fields.items():
            embed.add_field(name=name, value=value)

        if image is not None:
            embed.set_image(url=image)
        if footer is not None:
            embed.set_footer(footer)
        return await ctx.send(*args, embed=embed)

    # over-ridden
    def load_extension(self, *args, **kwargs):
        super().load_extension(*args, **kwargs)

    def run(self, *args, **kwargs):
        super().run(_token.get(), *args, **kwargs)

    async def close(self, *args, **kwargs):
        if self.is_closed():
            return

        print(f"Closing {self.user.name}...")
        await self.alert(status=Status.DOWN)

        if kwargs.pop("forced_close"):
            return await super(self.__class__, self).close()
        await super().close()

    async def on_disconnect(self):
        self.is_online = False

    async def on_message(self, message):
        try:
            ctx = await self.get_context(message)
        except Exception:
            ctx = None

        if all((self.received_love is False, message.guild is None,
                message.author.id in self.owner_ids, ctx is not None)):
            self.received_love = True
            await utils.react_with(ctx, emojis.BLUE_HEART)
        elif all((self.received_love, message.guild is None,
                  message.author.id in self.owner_ids, ctx is not None)):
            await utils.react_with(ctx, emojis.HEART)
        await self.process_commands(message)


if __name__ == '__main__':
    bot = GrottoBot()
    bot.run()
