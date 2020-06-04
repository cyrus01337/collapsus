"""Explanation"""
from enum import Enum
from enum import auto

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                   "rv:76.0) Gecko/20100101 Firefox/76.0,"),
    "Accept-Encoding": "gzip, deflate",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


class Owner(Enum):
    CYRUS = 668906205799907348
    GRADIS = 263694336040894465

    @classmethod
    def all(cls):
        return (cls.CYRUS.value, cls.GRADIS.value)


class Status(Enum):
    DOWN = auto()
    UP = auto()
