from typing import TypeVar

T = TypeVar("T")


def fset(*args: T) -> frozenset[T]:
    return frozenset(args)
