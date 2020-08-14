"""Explanation"""
from discord.ext import commands

# import prefix


class ModerationCog(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
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


def setup(bot):
    bot.add_cog(ModerationCog(bot))
