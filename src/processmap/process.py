from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from itertools import count

from .common import fset
from .graph import Edge, Graph, NodeId

__all__ = ["ProcessMap", "Process", "Series", "Union"]


class ProcessMap(ABC):
    @abstractmethod
    def to_subgraph(
        self, new_id: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        ...

    def to_graph(self) -> Graph:
        new_id = count().__next__
        return self.to_subgraph(new_id, new_id(), new_id())

    def __add__(self, other: ProcessMap) -> Series:
        return Series(self, other)

    def __or__(self, other: ProcessMap) -> Union:
        return Union(self, other)


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    duration: int

    def to_subgraph(
        self, new_id: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        return Graph(
            edges=fset(Edge(start, end, self.name, self.duration)),
            start=start,
            end=end,
        )


@dataclass(frozen=True)
class Series(ProcessMap):
    """
    Indicates relationship between two processes where B may start
    only after A is done
    """

    a: ProcessMap
    b: ProcessMap

    def to_subgraph(
        self, new_id: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        return Graph(
            self.b.to_subgraph(new_id, link := new_id(), end).edges
            | self.a.to_subgraph(new_id, start, link).edges,
            start,
            end,
        )


@dataclass(frozen=True)
class Union(ProcessMap):
    """
    Indicates two processes are part of the same process map.
    Overlapping pars are merged
    """
    a: ProcessMap
    b: ProcessMap

    def to_subgraph(
        self, new_id: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> Graph:
        return Graph(
            self.a.to_subgraph(new_id, start, end).edges
            | self.b.to_subgraph(new_id, start, end).edges,
            start,
            end,
        )
