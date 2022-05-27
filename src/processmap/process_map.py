from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

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
        start = Node(predecessors=frozenset())
        end = Node(
            predecessors=fset(
                (
                    Edge(
                        name=self.name,
                        min_duration=self.min_duration,
                        max_duration=self.max_duration,
                    ),
                    start,
                )
            )
        )
        return ProcessGraph(end=end)


def process(name: str, min_duration: int, max_duration: int | None = None) -> Process:
    return Process(name, min_duration, either(max_duration, min_duration))


@dataclass(frozen=True)
class SerialProcessMap(ProcessMap):
    processes: Sequence[ProcessMap]

    def to_dag(self) -> ProcessGraph:
        last_node = Node(predecessors=frozenset())
        for graph in map(lambda x: x.to_dag(), self.processes):
            z   graph.get_start()
            last_node = Node(predecessors=fset((edge, last_node)))
        return ProcessGraph(end=last_node)
