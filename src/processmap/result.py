from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    start: int
    end: int
