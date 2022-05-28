from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import NotImplementedType


@dataclass(frozen=True)
class Edge:
    start: Node
    end: Node
    name: str
    min_duration: int
    max_duration: int


@dataclass(frozen=True, eq=False)
class Node:
    # resources_to_request
    # resources_to_release

    def __repr__(self) -> str:
        return f"{type(self)}({id(self)})"


@dataclass(frozen=True, eq=False)
class ProcessGraph:
    """
    A connected directed acyclic graph meeting two criteria:
    - There is only one initial node (the source) (a node without incoming edges)
    - There is only one final node (the sink) (a node without outgoing edges)
    """

    edges: frozenset[Edge]
    start: Node = field(init=False)
    end: Node = field(init=False)

    def __post_init__(self) -> None:
        initial_nodes = {edge.start for edge in self.edges} - {
            edge.end for edge in self.edges
        }
        assert len(initial_nodes) == 1
        (start,) = initial_nodes
        object.__setattr__(self, "start", start)

        final_nodes = {edge.end for edge in self.edges} - {
            edge.start for edge in self.edges
        }
        assert len(final_nodes) == 1
        (end,) = final_nodes
        object.__setattr__(self, "end", end)

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, ProcessGraph):
            return NotImplemented

        mapping: dict[Node, Node] = {}
        for edge, other_edge in zip(self.edges, other.edges):
            if edge.start not in mapping:
                mapping[edge.start] = other_edge.start
            if edge.end not in mapping:
                mapping[edge.end] = other_edge.end

            if other_edge != replace(
                edge, start=mapping[edge.start], end=mapping[edge.end]
            ):
                return False
        else:
            return True
