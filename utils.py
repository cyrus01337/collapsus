"""Explanation"""
import os

import aiohttp

from constants import HEADERS


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


async def mystbin(message: str):
    url = "https://mystb.in"

    if message.endswith("\n") is False:
        message += "\n"

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        response = await session.post(f"{url}/documents", data=message)
        json = await response.json()
        key = json.get("key")

        return f"{url}/{key}"
