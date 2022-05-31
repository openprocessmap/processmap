from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from functools import reduce
from itertools import count

from processmap.process_graph import Edge, NodeId, ProcessGraph

from .helpers import fset  # TODO: one style of imports


class ProcessMap(ABC):
    @abstractmethod
    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> ProcessGraph:
        ...

    def to_graph(self) -> ProcessGraph:
        counter = count().__next__
        return self.to_subgraph(counter, counter(), counter())


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    duration: int

    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> ProcessGraph:
        return ProcessGraph(
            edges=fset(Edge(start, end, self.name, self.duration)),
            start=start,
            end=end,
        )


@dataclass(frozen=True)
class SerialProcessMap(ProcessMap):
    processes: tuple[ProcessMap, ...]

    def __post_init__(self) -> None:
        assert len(self.processes) > 0

    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> ProcessGraph:
        last = start
        graphs = []
        for p in self.processes[:-1]:
            subgraph = p.to_subgraph(counter, last, counter())
            graphs.append(subgraph)
            last = subgraph.end
        graphs.append(self.processes[-1].to_subgraph(counter, last, end))
        return ProcessGraph(
            reduce(
                frozenset.__or__,
                (g.edges for g in graphs),
                frozenset(),
            ),
            start,
            end,
        )


@dataclass(frozen=True)
class ParallelProcessMap(ProcessMap):
    processes: frozenset[ProcessMap]  # non-empty

    def __post_init__(self) -> None:
        assert len(self.processes) > 0

    def to_subgraph(
        self, counter: Callable[[], NodeId], start: NodeId, end: NodeId
    ) -> ProcessGraph:
        edges = [p.to_subgraph(counter, start, end).edges for p in self.processes]
        return ProcessGraph(reduce(frozenset.union, edges), start, end)
