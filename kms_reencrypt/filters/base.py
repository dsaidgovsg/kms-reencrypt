from enum import Enum
from typing import Callable, Iterable


class Filter:
    def process(self, bucket: str, key: str) -> bool:
        pass


class Match(str, Enum):
    FIRST = "first"
    ANY = "any"
    ALL = "all"
    NONE = "none"


def first(itr: Iterable[object]) -> bool:
    try:
        return next(itr)
    except StopIteration:
        return False


def none(itr: Iterable[object]) -> bool:
    try:
        next(itr)
        return True
    except StopIteration:
        return False


def get_match_pred(match: Match) -> Callable[[Iterable[object]], bool]:
    if match == Match.FIRST:
        return first
    elif match == Match.ANY:
        return any
    elif match == Match.ALL:
        return all
    elif match == Match.NONE:
        return none
    else:
        raise RuntimeError("Unexpected match type")
