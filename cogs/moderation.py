"""Explanation"""
from discord.ext import commands


class ModerationCog(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return True

    def validate_prefix(self, prefix: str):
        return True

    @commands.group(name="settings", invoke_without_subcommand=True)
    async def _settings(self, ctx):
        """Explanation"""
        message = ""
        settings = {
            "prefix": f"`{ctx.prefix}`"
        }

        for key, value in settings.items():
            message += f"**{key.title()}**: {value}\n"
        await ctx.send(message)

    @_settings.command()
    async def settings_prefix(self, ctx, prefix):
        message = (f"`{prefix}` is considered an invalid prefix and has not "
                   f"been set")

        if self.validate_prefix(prefix):
            message = f"Set prefix to: `{prefix}`"
            self.bot.set_prefix(prefix)
        await ctx.send(message)


def setup(bot):
    bot.add_cog(ModerationCog(bot))
