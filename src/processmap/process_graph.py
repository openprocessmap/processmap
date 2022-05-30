from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class EdgeInfo:
    name: str
    min_duration: int
    max_duration: int


@dataclass(frozen=True)
class ProcessGraph:
    """
    A connected directed acyclic graph meeting two criteria:
    - There is only one initial node (the source) (a node without incoming edges)
    - There is only one final node (the sink) (a node without outgoing edges)
    """

    edges: Mapping[tuple[int, int], EdgeInfo]
    first: int
    last: int
