from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass
from functools import reduce
from itertools import product

from .common import fset
from .errors import CircularDependencyError
from .graph import (
    DependencyEdge,
    Graph,
    ProcessEdge,
    ProcessNode,
    ReleaseNode,
    RequestNode,
)

__all__ = ["ProcessMap", "Process", "Seq", "Union", "Request", "Release"]

from .result import Result

ObjectId = int


class ProcessMap(ABC):
    def to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        try:
            return subgraphs[id(self)]
        except KeyError:
            graph = subgraphs[id(self)] = self._to_subgraph(subgraphs)
            return graph

    @abstractmethod
    def _to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        ...

    def to_graph(self) -> Graph:
        return self.to_subgraph(subgraphs={})

    @abstractmethod
    def run(self) -> Mapping[ProcessMap, Result]:
        ...

    @property
    @abstractmethod
    def processes(self) -> Set[ProcessMap]:
        ...

    def __rshift__(self, other: ProcessMap) -> Seq:
        return Seq(self, other)

    def __or__(self, other: ProcessMap) -> ProcessMap:
        """Create a merged union of this and another process map"""
        return Union(self, other)

    def using(self, resource: object, *additional_resources: object) -> ProcessMap:
        return WithResources(self, [resource, *additional_resources])


@dataclass(frozen=True)
class Process(ProcessMap):
    name: str
    duration: int

    def _to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        return Graph(
            nodes=fset(start := ProcessNode(), end := ProcessNode()),
            edges=fset(ProcessEdge(start, end, self.name, self.duration)),
            start=fset(start),
            end=fset(end),
        )

    def run(self) -> Mapping[ProcessMap, Result]:
        return {self: Result(0, self.duration)}

    @property
    def processes(self) -> Set[ProcessMap]:
        return {self}


@dataclass(frozen=True)
class Seq(ProcessMap):
    """
    Indicates relationship between two processes where B may start
    only after A is done
    """

    a: ProcessMap
    b: ProcessMap

    def __post_init__(self) -> None:
        if common_processes := self.a.processes & self.b.processes:
            raise CircularDependencyError(
                "Unable to create dependency between two process maps"
                "that have common processes.\n"
                "Common processes:\n\n" + "\n".join(map(repr, common_processes))
            )

    def _to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        graph_a = self.a.to_subgraph(subgraphs)
        graph_b = self.b.to_subgraph(subgraphs)
        links = {DependencyEdge(u, v) for u, v in product(graph_a.end, graph_b.start)}
        return Graph(
            nodes=graph_a.nodes | graph_b.nodes,
            edges=graph_a.edges | graph_b.edges | links,
            start=graph_a.start,
            end=graph_b.end,
        )

    def run(self) -> Mapping[ProcessMap, Result]:
        result_a = self.a.run()
        result_b = self.b.run()

        end_a = result_a[self.a].end

        return (
            result_a
            | {
                process: Result(result.start + end_a, result.end + end_a)
                for process, result in result_b.items()
            }
            | {self: Result(result_a[self.a].start, result_b[self.b].end + end_a)}
        )

    @property
    def processes(self) -> Set[ProcessMap]:
        return self.a.processes | self.b.processes | {self}


@dataclass(frozen=True)
class Union(ProcessMap):
    """
    Two processes which may or may not be related
    """

    a: ProcessMap
    b: ProcessMap

    def _to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        graph_a = self.a.to_subgraph(subgraphs)
        graph_b = self.b.to_subgraph(subgraphs)
        return Graph(
            nodes=graph_a.nodes | graph_b.nodes,
            edges=(edges := graph_a.edges | graph_b.edges),
            start=(graph_a.start | graph_b.start).difference(
                edge.end for edge in edges
            ),
            end=(graph_a.end | graph_b.end).difference(edge.start for edge in edges),
        )

    def run(self) -> Mapping[ProcessMap, Result]:
        ...


@dataclass(frozen=True)
class Request(ProcessMap):
    """
    A process that only completes once a resource has been granted
    """

    resource: object

    def _to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        return Graph(
            nodes=fset(node := RequestNode(requested_resource=self.resource)),
            edges=fset(),
            start=fset(node),
            end=fset(node),
        )

    def run(self) -> Mapping[ProcessMap, Result]:
        ...


@dataclass(frozen=True)
class Release(ProcessMap):
    """
    A process that releases a resource back to the resource pool and completes
    """

    resource: object

    def _to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        return Graph(
            nodes=fset(node := ReleaseNode(released_resource=self.resource)),
            edges=fset(),
            start=fset(node),
            end=fset(node),
        )

    def run(self) -> Mapping[ProcessMap, Result]:
        ...


@dataclass(frozen=True)
class WithResources(ProcessMap):
    """
    A process wrapping a nested process with the request and release of resources
    """

    process: ProcessMap
    resources: Sequence[object]  # at least one

    def __post_init__(self) -> None:
        assert len(self.resources) > 0

    def _to_subgraph(self, subgraphs: dict[ObjectId, Graph]) -> Graph:
        all_requests = reduce(Union.__call__, map(Request, self.resources))
        all_releases = reduce(
            Union.__call__,
            map(Release, reversed(self.resources)),
        )
        return (all_requests >> self.process >> all_releases).to_subgraph(subgraphs)

    def run(self) -> Mapping[ProcessMap, Result]:
        ...


# @dataclass(frozen=True)
# class WaitUntil(ProcessMap):
#     """
#     A process that only finishes after a specific time
#     on the simulation clock has passed
#     If it starts after this time it finishes immediately
#     """
#
#     earliest_start_time: int
#
#
# @dataclass(frozen=True)
# class Option(ProcessMap):
#     """
#     A process that can be skipped, depending on a condition
#     evaluated at the start of the wrapping process
#     """
#
#     condition: Callable[[], bool]
#     process: ProcessMap
#
#
# @dataclass(frozen=True)
# class Switch(ProcessMap):
#     """
#     A process that wraps two process
#     Depending on a condition evaluated at the start of the wrapping process
#     only one of the two processes will be executed and the other will be skipped
#
#     Should behave as:
#     Option(F, process1) | Option(lambda x: not F(), process2)
#     """
#
#     condition: Callable[[], bool]
#     process1: ProcessMap
#     process2: ProcessMap
