import enum
from collections import OrderedDict
from typing import Optional

import discord
from discord.ext import commands

_NAMES = {
    "material": "envname",
    "location": "loc",
    "max_level": "clev",
    "max_revocations": "rev",
    "last_grotto_level": "glev"
}


class Threshold:
    __slots__ = ("_hex", "min", "max")

    def __init__(self, *, min: int, max: int, hex: bool = False):
        self._hex = hex
        self.min = min
        self.max = max

    def is_hex(self):
        return self._hex


class Parameter:
    __slots__ = ("name", "value")

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def __repr__(self):
        return (f"<Parameter name={self.name} value={self.value}>")

    def to_dict(self):
        return {self.name: self.value}


class Flags(enum.Enum):
    PREFIX = [
        "clay",
        "rock",
        "granite",
        "basalt",
        "graphite",
        "iron",
        "copper",
        "bronze",
        "steel",
        "silver",
        "gold",
        "platinum",
        "ruby",
        "emerald",
        "sapphire",
        "diamond"
    ]
    MATERIAL = [
        "cave",
        "tunnel",
        "mine",
        "crevasse",
        "marsh",
        "lair",
        "icepit",
        "lake",
        "crater",
        "path",
        "snowhall",
        "moor",
        "dungeon",
        "crypt",
        "nest",
        "ruins",
        "tundra",
        "waterway",
        "world",
        "abyss",
        "maze",
        "glacier",
        "chasm",
        "void"
    ]
    SUFFIX = [
        "joy",
        "bliss",
        "glee",
        "doubt",
        "woe",
        "dolour",
        "regret",
        "bane",
        "fear",
        "dread",
        "hurt",
        "gloom",
        "doom",
        "evil",
        "ruin",
        "death"
    ]
    LEVEL = Threshold(min=1, max=99)
    TYPE = [
        "caves",
        "ruins",
        "ice",
        "water",
        "fire"
    ]
    LOCATION = Threshold(min=1, max=150, hex=True)
    BOSS = [
        "equinox",
        "nemean",
        "shogum",
        "trauminator",
        "elusid",
        "sir sanguinus",
        "atlas",
        "hammibal",
        "fowleye",
        "excalipurr",
        "tyrannosaurus wrecks",
        "greygnarl"
    ]
    MAX_LEVEL = Threshold(min=1, max=99)
    MAX_REVOCATION = Threshold(min=0, max=10)
    LAST_GROTTO_LEVEL = Threshold(min=0, max=99)

    @property
    def optional(self):
        return Optional[self.converter]

    def converter(self, argument):
        argument = argument.lower()
        name = self.name.lower()
        resolved = _NAMES.get(name, name)

        if isinstance(self.value, list):
            if argument not in self.value:
                raise commands.BadArgument(f"{argument} is an invalid {name}")
            return Parameter(resolved, self.value.index(argument) + 1)
        elif isinstance(self.value, Threshold):
            base = 10

            if self.value.is_hex():
                base = 16
            argument = int(argument, base=base)

            if not (self.value.min <= argument <= self.value.max):
                raise commands.BadArgument(f"{argument} is an invalid {name}")
            return Parameter(resolved, argument)
        raise commands.BadArgument(f"invalid datatype passed: {argument}")


class Grotto:
    def __init__(self, payload):
        self.details = OrderedDict()

        self._do_parsing(payload)

        # im sorry im a lazy shit
        for attr, value in self.details.items():
            setattr(self, attr, value)

    def __repr__(self):
        joined = (" ").join(f"{k}={v!r}" for k, v in self.details.items())

        return f"<Grotto {joined}>"

    def _do_parsing(self, payload):
        key = ""
        attrs = OrderedDict()

        for element in payload:
            data = str.strip(element.get())

            if not data:
                continue

            if data.endswith(":"):
                # found a title which acts as a key
                default = ""
                key = data[:-1]

                if len(key) > 1:
                    key = key.lower()

                # variable locations - list used to simplify tracking +
                # additions to
                if key == "Locations":
                    default = []
                attrs[key] = default
            else:
                # found a value - the current key determines whether the
                # value is set/appended
                value = attrs[key]
                append = f" {data}"

                # special-case insertion to make checking for special
                # floors easier
                if data == "Has a special floor":
                    attrs["special"] = True

                    continue
                elif isinstance(value, list):
                    append = [data]
                attrs[key] += append

        attrs.setdefault("special", False)

        for key, value in attrs.items():
            container = self.details

            # the key can be a chest type (A, B, etc.) which are stored
            # similarly to locations - OrderedDicts also ensure the
            # order of additions
            if len(key) == 1:
                container = self.details.setdefault("chests", OrderedDict())

            if isinstance(value, str):
                value = value.lstrip()
            container[key] = value


class Field:
    def __init__(self, name=None, value=None, inline=False):
        self.name = name
        self.value = value
        self.inline = inline


class Embed(discord.Embed):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        desc_alias_found = kwargs.get("desc", None)

        if desc_alias_found:
            kwargs["description"] = desc_alias_found

        super().__init__(*args, **kwargs)

        if fields:
            for field in fields:
                self.add_field(
                    name=field.name,
                    value=field.value,
                    inline=field.inline
                )
