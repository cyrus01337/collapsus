"""Explanation"""
import os


def clear_screen():
    return os.system(dict(nt="cls", posix="clear").get(os.name))


def flake8():
    return os.popen("flake8")


def multi_pop(iterable, *keys):
    for key in keys:
        value = iterable.pop(key, None)

        if value is not None:
            return value
    return None


async def react_with(ctx, *emojis):
    for emoji in emojis:
        await ctx.message.add_reaction(emoji)
