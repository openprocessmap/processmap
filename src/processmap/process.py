from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from itertools import count, product

from .common import fset
from .graph import Edge, Graph, NodeId

__all__ = ["ProcessMap", "Process", "Seq", "Union"]


ObjectId = int


class ProcessMap(ABC):
    @abstractmethod
    def to_subgraph(
        self, new_id: Callable[[], NodeId], subgraphs: dict[ObjectId, Graph]
    ) -> Graph:
        ...

    def to_graph(self) -> Graph:
        new_id = count().__next__
        return self.to_subgraph(new_id, subgraphs={})

    def __add__(self, other: ProcessMap) -> Seq:
        # TODO: make this a chaining operator to prevent overly nesting
        return Seq(self, other)

    def __rshift__(self, other: ProcessMap) -> Seq:
        # TODO: make this a chaining operator to prevent overly nesting
        return Seq(self, other)

    def __or__(self, other: ProcessMap) -> ProcessMap:
        "Create a merged union of this and another process map"
        return Union(self, other)

    # def __le__(self, other: ProcessMap) -> bool:
    #     "Whether other is a subset or equal of this process map"


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    duration: int

    def to_subgraph(
        self, new_id: Callable[[], NodeId], subgraphs: dict[ObjectId, Graph]
    ) -> Graph:
        # TODO: reconsider accessing cache here
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph = subgraphs[id(self)] = Graph(
                fset(
                    Edge(start := new_id(), end := new_id(), self.name, self.duration)
                ),
                start=fset(start),
                end=fset(end),
            )
            return graph

    # def __or__(self, other: ProcessMap) -> ProcessMap:
    #     if isinstance(other, Seq | Process):
    #         return other if self <= other else Union(self, other)
    #     return NotImplemented

    # def __le__(self, other: ProcessMap) -> bool:
    #     match other:
    #         case Process():
    #             return self == other
    #         case Seq(a, b):
    #             return self <= a or self <= b
    #         case _:
    #             return NotImplemented


@dataclass(frozen=True)
class Seq(ProcessMap):
    """
    Indicates relationship between two processes where B may start
    only after A is done
    """

    a: ProcessMap
    b: ProcessMap

    def to_subgraph(
        self, new_id: Callable[[], NodeId], subgraphs: dict[ObjectId, Graph]
    ) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph_a = self.a.to_subgraph(new_id, subgraphs)
            graph_b = self.b.to_subgraph(new_id, subgraphs)
            links = {
                Edge(u, v, "<seq>", 0)  # TODO: find a solution to ugly string
                for u, v in product(graph_a.end, graph_b.start)
            }
            graph = subgraphs[id(self)] = Graph(
                graph_b.edges | graph_a.edges | links,
                start=graph_a.start,
                end=graph_b.end,
            )
            return graph

    # def __or__(self, other: ProcessMap) -> ProcessMap:
    #     match other:
    #         case Process():
    #             return self if other <= self else Union(self, other)
    #         case Seq():
    #             # TODO: detect overlaps
    #             return Union(self, other)
    #     return NotImplemented

    # def __le__(self, p: ProcessMap) -> bool:
    #     return NotImplemented


@dataclass(frozen=True)
class Union(ProcessMap):
    """
    Two processes which may or may not be related
    """

    a: ProcessMap
    b: ProcessMap

    def to_subgraph(
        self, new_id: Callable[[], NodeId], subgraphs: dict[ObjectId, Graph]
    ) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph_a = self.a.to_subgraph(new_id, subgraphs)
            graph_b = self.b.to_subgraph(new_id, subgraphs)
            graph = subgraphs[id(self)] = Graph(
                edges := graph_b.edges | graph_a.edges,
                start=(graph_a.start | graph_b.start)
                - frozenset({edge.end for edge in edges}),
                end=(graph_a.end | graph_b.end)
                - frozenset({edge.start for edge in edges}),
            )
            return graph

    # def __or__(self, other: ProcessMap) -> ProcessMap:
    #     raise NotImplementedError()
