from abc import ABC, abstractmethod
from functools import reduce
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from itertools import count

from processmap.helpers import either
from processmap.process_graph import EdgeInfo, NodeId, ProcessGraph


class ProcessMap(ABC):
    @abstractmethod
    def to_subgraph(self, counter: Callable[[], NodeId], start: NodeId) -> ProcessGraph:
        ...

    def to_graph(self) -> ProcessGraph:
        counter = count().__next__
        return self.to_subgraph(counter, counter())


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    min_duration: int
    max_duration: int

    def to_subgraph(self, counter: Callable[[], NodeId], start: NodeId) -> ProcessGraph:
        end = counter()

        return ProcessGraph(
            edges={
                (start, end): EdgeInfo(self.name, self.min_duration, self.max_duration)
            },
            first=start,
            last=end,
        )


def process(name: str, min_duration: int, max_duration: int | None = None) -> Process:
    return Process(name, min_duration, either(max_duration, min_duration))


@dataclass(frozen=True)
class SerialProcessMap(ProcessMap):
    processes: Sequence[ProcessMap]

    def to_subgraph(self, counter: Callable[[], NodeId], start: NodeId) -> ProcessGraph:
        last = start
        graphs = []
        for p in self.processes:
            subgraph = p.to_subgraph(counter, last)
            graphs.append(subgraph)
            last = subgraph.last
        return ProcessGraph(
            reduce(
                dict.__or__, (g.edges for g in graphs), {}  # type: ignore[arg-type]
            ),
            start,
            last,
        )
