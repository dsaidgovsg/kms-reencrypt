from enum import Enum


class Filter:
    def process(self, bucket: str, key: str) -> bool:
        pass


class Match(str, Enum):
    FIRST = "first"
    ANY = "any"
    ALL = "all"
