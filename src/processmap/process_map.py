from __future__ import annotations

from collections.abc import Set
from dataclasses import dataclass

from processmap.either import either


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


@dataclass(frozen=True)
class Process:
    name: str
    min_duration: int
    max_duration: int

    def to_dag(self) -> ProcessGraph:
        start = Node(predecessors=frozenset())
        end = Node(
            predecessors=frozenset(
                [
                    (
                        Edge(
                            name=self.name,
                            min_duration=self.min_duration,
                            max_duration=self.max_duration,
                        ),
                        start,
                    )
                ]
            )
        )
        return ProcessGraph(end=end)


def process(name: str, min_duration: int, max_duration: int | None = None) -> Process:
    return Process(name, min_duration, either(max_duration, min_duration))
