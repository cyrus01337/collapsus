from discord.ext import commands

from base import custom


class Information(custom.Cog):
    class Setting(commands.Converter):
        async def convert(self, ctx, argument):
            argument = argument.lower()
            settings = ctx.bot.db.Settings

            if argument in settings.VALID:
                return argument
            raise commands.BadArgument(f'invalid setting "{argument}"')

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def settings(self, ctx, setting: Setting, value: bool):
        settings_found = self.bot.db.settings.get(ctx.author.id, None)

        if not settings_found:
            pass
        settings_found[setting] = value

        await ctx.send(f"Successfully set setting.{setting} to {value}")


def setup(bot):
    bot.add_cog(Information(bot))
