from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from functools import reduce
from itertools import product

from .common import fset
from .graph import (
    DependencyEdge,
    Graph,
    ProcessEdge,
    ProcessNode,
    ReleaseNode,
    RequestNode,
)

__all__ = ["ProcessMap", "Process", "Seq", "Union"]


ObjectId = int


class ProcessMap(ABC):
    @abstractmethod
    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        ...

    def to_graph(self) -> Graph:
        return self.to_subgraph(subgraphs={})

    def __rshift__(self, other: ProcessMap) -> Seq:
        # TODO: make this a chaining operator to prevent overly nesting
        return Seq(self, other)

    def __or__(self, other: ProcessMap) -> ProcessMap:
        """Create a merged union of this and another process map"""
        return Union(self, other)

    def using(self, *attr: object) -> ProcessMap:
        return WithResources(self, attr)


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    duration: int

    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        # TODO: reconsider accessing cache here
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph = subgraphs[id(self)] = Graph(
                nodes=fset(start := ProcessNode(), end := ProcessNode()),
                edges=fset(ProcessEdge(start, end, self.name, self.duration)),
                start=fset(start),
                end=fset(end),
            )
            return graph


@dataclass(frozen=True)
class Seq(ProcessMap):
    """
    Indicates relationship between two processes where B may start
    only after A is done
    """

    a: ProcessMap
    b: ProcessMap

    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph_a = self.a.to_subgraph(subgraphs)
            graph_b = self.b.to_subgraph(subgraphs)
            links = {
                DependencyEdge(u, v) for u, v in product(graph_a.end, graph_b.start)
            }
            graph = subgraphs[id(self)] = Graph(
                nodes=graph_a.nodes | graph_b.nodes,
                edges=graph_a.edges | graph_b.edges | links,
                start=graph_a.start,
                end=graph_b.end,
            )
            return graph


@dataclass(frozen=True)
class Union(ProcessMap):
    """
    Two processes which may or may not be related
    """

    a: ProcessMap
    b: ProcessMap

    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph_a = self.a.to_subgraph(subgraphs)
            graph_b = self.b.to_subgraph(subgraphs)
            graph = subgraphs[id(self)] = Graph(
                nodes=graph_a.nodes | graph_b.nodes,
                edges=(edges := graph_a.edges | graph_b.edges),
                start=(graph_a.start | graph_b.start)
                - frozenset({edge.end for edge in edges}),
                end=(graph_a.end | graph_b.end)
                - frozenset({edge.start for edge in edges}),
            )
            return graph


@dataclass(frozen=True)
class Request(ProcessMap):
    """
    A process that only completes once a resource has been granted
    """

    resource: object

    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph = subgraphs[id(self)] = Graph(
                nodes=fset(node := RequestNode(requested_resource=self.resource)),
                edges=fset(),
                start=fset(node),
                end=fset(node),
            )
            return graph


@dataclass(frozen=True)
class Release(ProcessMap):
    """
    A process that releases a resource back to the resource pool and completes
    """

    resource: object

    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph = subgraphs[id(self)] = Graph(
                nodes=fset(node := ReleaseNode(released_resource=self.resource)),
                edges=fset(),
                start=fset(node),
                end=fset(node),
            )
            return graph


@dataclass(frozen=True)
class WithResources(ProcessMap):
    """
    A process wrapping a nested process with the request and release of resources
    """

    process: ProcessMap
    resources: Sequence[object]

    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            if len(self.resources) == 1:
                graph = subgraphs[id(self)] = self.process.to_subgraph(subgraphs)
                return graph

            all_requests = reduce(ProcessMap.__or__, map(Request, self.resources))
            all_releases = reduce(
                ProcessMap.__or__, map(Release, reversed(self.resources))
            )

            graph = subgraphs[id(self)] = (
                all_requests >> self.process >> all_releases
            ).to_subgraph(subgraphs)
            return graph
