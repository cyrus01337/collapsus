"""Explanation"""
import re

import discord
from discord.ext import commands
from discord.ext import flags
from discord.ext import menus

import prefix
import quotes
import utils


class QuoteSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=10)

    async def format_page(self, menu, entries):
        start = menu.current_page * self.per_page + 1
        enumeration = enumerate(entries, start=start)
        return ("\n").join(f"`{i})` {v}" for i, v in enumeration)


class QuotesCog(commands.Cog, name="Quotes System"):
    def __init__(self, bot):
        self.bot = bot
        self.markdown = re.compile(r"[\*_`~]")

        self.bot.loop.create_task(quotes.init())

    @flags.add_flag("name", nargs="+")
    @flags.add_flag("--raw", action="store_true")
    @flags.group(aliases=["q"], usage=f"{prefix.DEFAULT}quote test",
                 invoke_without_command=True)
    async def quote(self, ctx, **flags):
        """
        Make references to previously made statements with quote add
        """
        name = (" ").join(flags.get("name"))
        original = await quotes.resolve_alias(name)
        message = await quotes.get("quote", name=name)

        if flags.get("raw"):
            url = await utils.mystbin(message)
            message = f"<{url}>"
        else:
            message = discord.utils.escape_mentions(message)

        await quotes.increment(ctx.author.id, original or name)
        await ctx.send(message)

    @quote.command(name="add",
                   usage=f'{prefix.DEFAULT}quote add BQ BQ stands for...\n'
                         f'{prefix.DEFAULT}quote add "what is mks" They...')
    async def quote_add(self, ctx, name, *, quote):
        """
        Create a quote to reference later
        """
        message = "Quotes cannot be named with markdown"

        if self.markdown.search(name) is None:
            message = f'Added new quote "{name}"'
            quote = discord.utils.escape_mentions(quote)

            await quotes.add(ctx.author.id, name, quote)
        await ctx.send(message)

    @quote.command(name="edit", aliases=["modify"],
                   usage=f"{prefix.DEFAULT}quote edit test WIP")
    async def quote_edit(self, ctx, name, *, quote):
        """
        Make changes to an existing quote you've made
        """
        await quotes.edit(ctx.author.id, name, quote=quote)
        await ctx.send(f'Edited "{name}"')

    @quote.command(name="remove", aliases=["delete"],
                   usage=f"{prefix.DEFAULT}quote remove test")
    async def quote_remove(self, ctx, *, name):
        """
        Delete an owned quote
        """
        check = quotes.owned_by
        permissions = ctx.author.guild_permissions

        if permissions.administrator or permissions.manage_guild:
            check = None
        await quotes.remove(ctx.author.id, name, check=check)
        await ctx.send(f'Removed quote "{name}"')

    @quote.command(name="list",
                   usage=f"{prefix.DEFAULT}quote list\n"
                         f"{prefix.DEFAULT}quote list @Gradis#6666")
    async def quote_list(self, ctx, member: discord.Member = None):
        """
        Display all quotes created by the member given (defaults to you
        if the member is not given)
        """
        member = member or ctx.author
        names = await quotes.get_all(member.id, "name")

        if names is None:
            pronoun = "You" if member == ctx.author else "They"
            await ctx.send(f"{pronoun} do not have any quotes")
        else:
            menu = menus.MenuPages(
                source=QuoteSource(names),
                timeout=60.0,
                clear_reactions_after=True
            )
            await menu.start(ctx)

    @quote.command(name="alias",
                   usage=f'{prefix.DEFAULT}quote alias test test1\n'
                         f'{prefix.DEFAULT}quote alias "what is mks" mks')
    async def quote_alias(self, ctx, name, *, alias):
        """
        Set a nickname for a quote to be referenced by (multiple can be
        assigned)
        """
        await quotes.add_alias(name, alias)
        await ctx.send(f'Added alias "{alias}" to "{name}"')

    # @quote.command(name="info", aliases=["resolve"],
    #                usage=f"{prefix.DEFAULT}quote info what is mks")
    # async def quote_info(self, ctx, name):
    #     """
    #     Display quote information, such as the owner of the quote and
    #     how many times it's been used
    #     """
    #     name = await quotes.resolve_alias(name)
    #     args = ("author_id", "uses")
    #     author_id, uses = await quotes.get_all(ctx.author.id, *args)
    #     print(author_id, type(author_id))
    #     # author = self.bot.get_user(author_id)


def setup(bot):
    bot.add_cog(QuotesCog(bot))
