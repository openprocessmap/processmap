from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from itertools import count

from processmap.helpers import either
from processmap.process_graph import EdgeInfo, NodeId, ProcessGraph


class ProcessMap(ABC):
    @abstractmethod
    def to_subgraph(self, counter: Callable[[], NodeId]) -> ProcessGraph:
        ...

    def to_graph(self) -> ProcessGraph:
        return self.to_subgraph(count().__next__)


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    min_duration: int
    max_duration: int

    def to_subgraph(self, counter: Callable[[], NodeId]) -> ProcessGraph:
        start = counter()
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


def _replace_node(
    edges: Mapping[tuple[int, int], EdgeInfo], old_node: int, new_node: int
) -> Mapping[tuple[int, int], EdgeInfo]:
    return {
        (new_node if u == old_node else u, new_node if v == old_node else v): edge_info
        for (u, v), edge_info in edges.items()
    }


@dataclass(frozen=True)
class SerialProcessMap(ProcessMap):
    processes: Sequence[ProcessMap]

    def to_subgraph(self, counter: Callable[[], NodeId]) -> ProcessGraph:
        if len(self.processes) < 1:
            # no graphs
            return ProcessGraph(edges={}, first=0, last=0)

        graphs = list(map(lambda x: x.to_subgraph(counter), self.processes))

        # first graph
        edges = dict(graphs[0].edges)
        first = graphs[0].first
        last = graphs[0].last

        # other graphs
        for graph in graphs[1:]:
            edges |= _replace_node(graph.edges, graph.first, last)
            last = graph.last
        return ProcessGraph(edges, first, last)
