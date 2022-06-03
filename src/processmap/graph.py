from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass

__all__ = ["Graph", "Node", "ProcessNode", "ProcessEdge", "DependencyEdge"]


class GraphObject(ABC):
    @abstractmethod
    def attributes(self) -> Mapping[str, object]:
        ...


class BaseNode(GraphObject):
    def attributes(self) -> Mapping[str, object]:
        return dict()

    def __str__(self) -> str:
        return f"{type(self).__name__}({id(self)})"


@dataclass(frozen=True, eq=False)
class ProcessNode(BaseNode):
    def attributes(self) -> Mapping[str, object]:
        return dict()


@dataclass(frozen=True, eq=False)
class RequestNode(BaseNode):
    requested_resource: object

    def attributes(self) -> Mapping[str, object]:
        return {"requested_resource": self.requested_resource}


@dataclass(frozen=True, eq=False)
class ReleaseNode(BaseNode):
    released_resource: object

    def attributes(self) -> Mapping[str, object]:
        return {"released_resource": self.released_resource}


Node = ProcessNode | RequestNode | ReleaseNode


@dataclass(frozen=True)
class BaseEdge(GraphObject):
    start: Node
    end: Node

    def attributes(self) -> Mapping[str, object]:
        return dict()

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.start} -> {self.end})"


@dataclass(frozen=True)
class ProcessEdge(BaseEdge):
    name: str
    duration: int

    def attributes(self) -> Mapping[str, object]:
        return {"name": self.name, "duration": self.duration}


@dataclass(frozen=True)
class DependencyEdge(BaseEdge):
    def attributes(self) -> Mapping[str, object]:
        return dict()


Edge = ProcessEdge | DependencyEdge


@dataclass(frozen=True)
class Graph:
    nodes: frozenset[Node]
    edges: frozenset[Edge]

    # TODO: reconsider if we want this duplicate info
    start: frozenset[Node]
    end: frozenset[Node]

    def union(self, other: Graph) -> Graph:
        return Graph(
            nodes=self.nodes | other.nodes,
            edges=(edges := self.edges | other.edges),
            start=(self.start | other.start) - frozenset(edge.end for edge in edges),
            end=(self.end | other.end) - frozenset(edge.start for edge in edges),
        )

    def __or__(self, other: Graph) -> Graph:
        return self.union(other)
