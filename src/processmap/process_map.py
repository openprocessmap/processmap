from abc import ABC, abstractmethod
from collections.abc import Sequence, Set
from dataclasses import dataclass, replace

from processmap.helpers import either, fset
from processmap.process_graph import Edge, Node, ProcessGraph


class ProcessMap(ABC):
    @abstractmethod
    def to_dag(self) -> ProcessGraph:
        ...


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    min_duration: int
    max_duration: int

    def to_dag(self) -> ProcessGraph:
        return ProcessGraph(
            fset(Edge(Node(), Node(), self.name, self.min_duration, self.max_duration))
        )


def process(name: str, min_duration: int, max_duration: int | None = None) -> Process:
    return Process(name, min_duration, either(max_duration, min_duration))


@dataclass(frozen=True)
class SerialProcessMap(ProcessMap):
    processes: Sequence[ProcessMap]

    def to_dag(self) -> ProcessGraph:
        graphs = map(lambda x: x.to_dag(), self.processes)
        edges: Set[Edge] = set()
        last_node: Node | None = None
        for graph in graphs:
            if last_node:
                edges |= {
                    replace(edge, start=last_node)
                    for edge in graph.edges
                    if edge.start == graph.start
                } | {edge for edge in graph.edges if edge.start != graph.start}
            else:
                edges = graph.edges
            last_node = graph.end
        return ProcessGraph(frozenset(edges))
