import enum
from collections import namedtuple, OrderedDict

from discord.ext import commands

Parameter = namedtuple("Parameter", "name value")
_NAMES = {
    "material": "envname",
    "location": "loc",
    "hl": "clev",
    "revocation": "rev",
    "hgl": "glev"
}


class Threshold:
    def __init__(self, *, min: int, max: int, hex: bool = False):
        self._hex = hex
        self.min = min
        self.max = max

    def is_hex(self):
        return self._hex


class Parameter:
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
    HL = Threshold(min=1, max=99)
    REVOCATION = Threshold(min=0, max=10)
    HGL = Threshold(min=0, max=99)

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
        key = None
        attrs = OrderedDict()
        self._details = OrderedDict()

        for element in payload:
            data = str.strip(element.get())

            if not data:
                continue

            if data.endswith(":"):
                default = ""
                key = data.rstrip(":")

                if len(key) > 1:
                    key = key.lower()

                if key == "Locations":
                    default = []
                attrs[key] = default
            else:
                value = attrs[key]
                append = f" {data}"

                if isinstance(value, list):
                    append = [data]
                attrs[key] += append

        self._details = attrs.copy()

        for key, value in attrs.items():
            if isinstance(value, str):
                self._details[key] = value.lstrip()

        self._setup_attribs()

    def __repr__(self):
        joined = (" ").join(f"{k}={v!r}" for k, v in self._details.items())

        return f"<Grotto {joined}>"

    @property
    def details(self):
        return self._details.items()

    def _setup_attribs(self):
        for attr, value in self.details:
            setattr(self, attr, value)
