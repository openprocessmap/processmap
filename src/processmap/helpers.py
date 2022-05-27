from typing import TypeVar

T = TypeVar("T")


def either(x: T | None, b: T) -> T:
    if x is not None:
        return x
    else:
        return b


def fset(*args: T) -> frozenset[T]:
    return frozenset(args)
