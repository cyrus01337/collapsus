from typing import Optional

import discord
from discord.ext import commands

from base import custom
from errors import QuoteException


class Quotes(custom.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_privileged(self, ctx):
        return (
            ctx.guild and
            ctx.author.guild_permissions.manage_guild or
            ctx.author.id == ctx.guild.owner_id
        )

    @commands.group(invoke_without_command=True)
    async def quote(self, ctx, *, name):
        quote_found = await self.bot.db.get_quote(name=name)

        if not quote_found:
            raise QuoteException(f'Quote "{name}" not found')

        escaped = discord.utils.escape_mentions(quote_found.content)

        await ctx.send(escaped)

    @quote.command(name="add")
    async def quote_add(self, ctx, name, *, content):
        quote_found = await self.bot.db.get_quote(name=name)

        if quote_found:
            raise QuoteException(f'Quote "{name}" already exists')

        await self.bot.db.add_quote(
            name,
            content,
            ctx.author.id
        )
        await ctx.send(f'Successfully created quote "{name}"')

    @quote.command(name="raw")
    async def quote_raw(self, ctx, name):
        cleaners = [
            discord.utils.escape_mentions,
            discord.utils.escape_markdown
        ]
        quote_found = await self.bot.db.get_quote(name=name)

        if not quote_found:
            raise QuoteException(f'Quote "{name}" not found')

        raw = quote_found.content

        for clean in cleaners:
            raw = clean(raw)

        await ctx.send(raw)

    @quote.command(name="update")
    async def quote_update(self, ctx, name, *, content):
        is_owner = await self.bot.db.owns_quote(ctx.author.id, name)
        is_privileged = self.is_privileged(ctx)

        if not (is_owner or is_privileged):
            raise QuoteException("You do not own this quote!")
        await self.bot.db.update_quote(name, content)
        await ctx.send(f'Successfully updated "{name}"')

    @quote.command(name="remove")
    async def quote_remove(self, ctx, *, name):
        is_owner = await self.bot.db.owns_quote(ctx.author.id, name)
        is_privileged = self.is_privileged(ctx)

        print(is_owner, is_privileged, not (is_owner or is_privileged))
        if not (is_owner or is_privileged):
            raise QuoteException("You do not own this quote!")
        await self.bot.db.remove_quote(name)
        await ctx.send(f'Successfully removed "{name}"')

    @quote.command(name="list")
    async def quote_list(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        quotes_found = await self.bot.db.get_all_quotes(member.id)

        if not quotes_found:
            who = "They"

            if ctx.author == member:
                who = "You"
            raise QuoteException(f"{who} do not own any quotes!")

        content = "\n".join(
            f"{i}) {quote.name}"
            for i, quote in enumerate(quotes_found, start=1)
        )

        await ctx.send(content)

    @commands.command()
    async def quotes(self, ctx, member: Optional[discord.Member]):
        await self.bot.alias_to("quote list", ctx, member)


def setup(bot):
    bot.add_cog(Quotes(bot))
