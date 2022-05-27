from __future__ import annotations

from collections.abc import Set
from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    name: str
    min_duration: int
    max_duration: int


@dataclass(frozen=True)
class Node:
    # resources_to_request
    # resources_to_release
    predecessors: Set[tuple[Edge, Node]]


@dataclass(frozen=True)
class ProcessGraph:
    """
    A connected directed acyclic graph meeting two criteria:
    - There is only one initial node (the source) (a node without incoming edges)
    - There is only one final node (the sink) (a node without outgoing edges)
    """

    end: Node

    def get_start(self) -> Node:
        x = self.end
        while x.predecessors:
            assert len(x.predecessors) == 1
            x = list(x.predecessors)[0][0]
        return x
