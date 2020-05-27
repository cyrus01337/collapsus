"""Discord bot base"""
import os

import discord
from discord.ext import commands

import emojis
import prefix
import utils
import _token
from constants import Owner


class GrottoBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(case_insensitive=True, reconnect=True,
                         **prefix.as_kwarg())
        self.owner_ids = Owner.all()

        self.is_online = False
        self.received_love = False
        self.invite_perms = discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            embed_links=True
        )
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

        for file in self.get_cog_filenames():
            self.load_extension(f"cogs.{file}")

    # helper methods
    def get_cog_filenames(self):
        ret = []

        for name in os.listdir("./cogs"):
            if name.endswith(".py"):
                ret.append(name[:-3])
        return ret

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

    async def setup(self):
        activity = discord.Activity(type=discord.ActivityType.listening,
                                    name=f"{prefix.DEFAULT} and pings!")

        utils.clear_screen()
        print(self.user.name, end="\n\n")
        await self.change_presence(activity=activity)

        for owner_id in self.owner_ids:
            owner = self.get_user(owner_id)

            if owner is not None:
                await owner.send("I'm up Dad")

    # over-ridden
    def run(self, *args, **kwargs):
        super().run(_token.get(), *args, **kwargs)

    async def on_disconnect(self):
        self.is_online = False

    async def on_ready(self):
        if self.is_online is False:
            self.is_online = True

            if getattr(self, "invite", None) is None:
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
            await self.setup()

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
