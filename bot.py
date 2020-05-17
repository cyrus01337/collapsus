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
                         command_prefix=prefix.get())
        self.owner_ids = (
            Owner.DJ.value,
            Owner.GRADIS.value
        )

        self.initialised = False
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
                "utils": (
                    ("store token settings when encrypting, retrieve token "
                     "settings as decrypting catalyst "),
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

    # over-ridden
    def run(self, *args, **kwargs):
        super().run(_token.get(), *args, **kwargs)

    async def on_ready(self):
        if self.initialised:
            return
        self.initialised = True
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

        activity = discord.Activity(type=discord.ActivityType.listening,
                                    name=f'"{prefix.DEFAULT}" and pings!')

        utils.clear_screen()
        print(self.user.name, end="\n\n")
        await self.change_presence(activity=activity)

        for owner_id in (Owner.CYRUS, Owner.GRADIS):
            owner = self.get_user(owner_id)

            if owner is not None:
                owner.send("I'm up Dad")

    async def on_message(self, message):
        if all((self.received_love is False, message.guild is None,
                message.author.id in self.owner_ids)):
            ctx = await self.get_context(message)
            await utils.react_with(ctx, emojis.HEART)
        await self.process_commands(message)


if __name__ == '__main__':
    bot = GrottoBot()
    bot.run()
