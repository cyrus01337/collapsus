"""Explanation"""
import random
import string
import typing

from discord.ext import commands

import emojis
import prefix


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {
            "chest": ("SABCDEFGHI")[::-1],
            "grotto": ("SABCDEFGHIJK")[::-1]
        }
        self.details = {
            "Gender": ("Male", "Female"),
            "Body Type": 5,
            "Hairstyle": 10,
            "Hair Colour": ("Dark Brown", "Light Brown", "Red", "Pink",
                            "Yellow", "Green", "Dark Blue", "Purple",
                            "Light Blue", "Grey"),
            "Face": 10,
            "Skin Colour": 8,
            "Eye Colour": ("Black", "Brown", "Red", "Yellow",
                           "Green", "Blue", "Purple", "Grey"),
            "Name": 8
        }

    def generate_rand_char(self):
        chosen = {}

        for key, options in self.details.items():
            if isinstance(options, int):
                value = ""

                if key == "Name":
                    for _ in range(random.randint(1, options)):
                        value += random.choice(string.ascii_lowercase)
                    value = value.title()
                else:
                    value = f"Type {random.randint(1, options)}"
            else:
                value = random.choice(options)
            chosen.setdefault(key, value)
        return chosen

    async def _resolve(self, ctx, medium: str, index: typing.Union[int, str]):
        medium = medium.lower()
        data = self.data.get(medium)
        message = "**Rank**: `{letter} ({number})`"

        if medium not in self.data.keys():
            return

        if isinstance(index, int) and index > 0 and index < 13:
            letter = data[index-1]
            message = message.format(letter=letter, number=index)
        elif isinstance(index, str):
            index = index.upper()

            if index not in data:
                return
            number = data.index(index) + 1
            message = message.format(letter=index, number=number)
        else:
            return
        await ctx.send(message)

    @commands.command(name="prefix")
    async def _prefix(self, ctx):
        """Explanation"""
        await ctx.send(f"The prefix is `{prefix.DEFAULT}` or you can mention "
                       f"me! E.g. `{prefix.DEFAULT} ping` or "
                       f"{self.bot.user.mention}` ping`")

    @commands.command()
    async def ping(self, ctx):
        """Explanation"""
        await ctx.send(f"{emojis.PING_PONG} **Pong!** "
                       f"{int(self.bot.latency * 1000):,}ms.")

    @commands.group(invoke_without_subcommand=True)
    async def resolve(self, ctx, medium, index: typing.Union[int, str]):
        """Explanation"""
        await self._resolve(ctx, medium=medium, index=index)

    @commands.group(invoke_without_subcommand=True)
    async def random(self, ctx):
        """Explanation"""
        message = ""
        rand_details = self.generate_rand_char()

        for key, value in rand_details.items():
            message += f"**{key}**: {value}\n"
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Information(bot))
