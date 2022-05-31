from dataclasses import dataclass

NodeId = int


@dataclass(frozen=True)
class Edge:
    start: NodeId
    end: NodeId
    name: str
    duration: int


@dataclass(frozen=True)
class ProcessGraph:
    """
    A connected directed acyclic graph meeting two criteria:
    - There is only one initial node (the source) (a node without incoming edges)
    - There is only one final node (the sink) (a node without outgoing edges)
    """

    edges: frozenset[Edge]
    start: NodeId
    end: NodeId
