from typing import Optional

from discord.ext import commands

import checks
from base import custom


class Information(custom.Cog):
    class Setting(commands.Converter):
        async def convert(self, ctx, argument):
            argument = argument.lower()

            if argument in ctx.bot.db.VALID_SETTINGS:
                return argument
            raise commands.BadArgument(f'{argument} is an invalid setting')

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return checks.require_settings(ctx)

    @commands.group(aliases=["setting"], invoke_without_command=True)
    async def settings(self,
                       ctx,
                       setting: Optional[Setting] = None,
                       value: Optional[bool] = None):
        translation = {True: "on"}

        if not setting and not value:
            settings_found = self.bot.db.settings[ctx.author.id]
            embed = custom.Embed(title="Settings", desc=str(ctx.author))

            for name, value in settings_found:
                name = name.title()

                if isinstance(value, bool):
                    value = translation.get(value, "off")

                embed.add_field(name=name, value=value)
            await ctx.send(embed=embed)
        else:
            settings_found = self.bot.db.settings[ctx.author.id]
            settings_found[setting] = value

            await ctx.send(f"Successfully set `settings.{setting}` to {value}")


def setup(bot):
    bot.add_cog(Information(bot))
