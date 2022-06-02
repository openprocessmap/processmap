from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from functools import reduce
from itertools import count

from .common import fset  # TODO: one style of imports
from .graph import Edge, Graph, NodeId

__all__ = ["ProcessMap", "Process", "Series", "Union"]


class ProcessMap(ABC):
    @abstractmethod
    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        ...

    def to_graph(self) -> Graph:
        counter = count().__next__
        return self.to_subgraph(counter, counter(), counter())

    def __add__(self, other: ProcessMap) -> Series:
        return Series((self, other))

    def __or__(self, other: ProcessMap) -> Union:
        return Union((self, other))


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    duration: int

    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        return Graph(
            edges=fset(Edge(start, end, self.name, self.duration)),
            start=start,
            end=end,
        )


@dataclass(frozen=True)
class Series(ProcessMap):
    processes: tuple[ProcessMap, ...]

    def __post_init__(self) -> None:
        assert len(self.processes) > 0

    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        last = start
        edges: set[Edge] = set()
        for p in self.processes[:-1]:
            subgraph = p.to_subgraph(counter, last, counter())
            edges |= subgraph.edges
            last = subgraph.end
        edges |= self.processes[-1].to_subgraph(counter, last, end).edges
        return Graph(frozenset(edges), start, end)

    def __add__(self, other: ProcessMap) -> Series:
        return Series((*self.processes, other))


@dataclass(frozen=True)
class Union(ProcessMap):
    processes: tuple[ProcessMap, ...]  # non-empty

    def __post_init__(self) -> None:
        assert len(self.processes) > 0

    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        edges = [p.to_subgraph(counter, start, end).edges for p in self.processes]
        return Graph(reduce(frozenset.union, edges), start, end)

    def __or__(self, other: ProcessMap) -> Union:
        return Union((*self.processes, other))
