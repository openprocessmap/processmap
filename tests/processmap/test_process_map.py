import pytest

from processmap.helpers import fset
from processmap.process_graph import Edge, ProcessGraph
from processmap.process_map import (
    ParallelProcessMap,
    Process,
    ProcessMap,
    SerialProcessMap,
)
from tests.processmap.process_graph_equal import process_graphs_isomorphic


@pytest.fixture
def process_map() -> ProcessMap:
    a = Process("A", 1)
    b = Process("B", 3)
    c = SerialProcessMap((a, b))
    e = Process("E", 5)
    return SerialProcessMap((c, e))


def test_process_to_graph() -> None:
    result = Process("test", 1).to_graph()
    expected = ProcessGraph(edges=fset(Edge(100, 101, "test", 1)), start=100, end=101)
    assert process_graphs_isomorphic(result, expected)


def test_process_to_graph_unequal() -> None:
    result = Process("test", 1).to_graph()
    expected = ProcessGraph(edges=fset(Edge(100, 101, "test", 2)), start=100, end=101)
    assert not process_graphs_isomorphic(result, expected)


def test_serial_process_empty_not_allowed() -> None:
    with pytest.raises(AssertionError):
        SerialProcessMap(())


def test_serial_process_to_process_graph_1() -> None:
    a = Process("A", 1)
    s = SerialProcessMap((a,))

    expected = ProcessGraph(edges=fset(Edge(0, 1, "A", 1)), start=0, end=1)
    result = s.to_graph()
    assert process_graphs_isomorphic(result, expected)


def test_serial_process_to_process_graph() -> None:
    a = Process("A", 1)
    b = Process("B", 3)
    c = SerialProcessMap((a, b))
    e = Process("E", 5)
    s = SerialProcessMap((c, e))

    expected = ProcessGraph(
        edges=fset(
            Edge(0, 1, "A", 1),
            Edge(1, 2, "B", 3),
            Edge(2, 3, "E", 5),
        ),
        start=0,
        end=3,
    )
    result = s.to_graph()

    assert process_graphs_isomorphic(result, expected)


def test_parallel_process_empty_not_allowed() -> None:
    with pytest.raises(AssertionError):
        ParallelProcessMap(frozenset())


def test_parallel_process_to_process_graph_single(process_map: ProcessMap) -> None:
    assert process_graphs_isomorphic(
        ParallelProcessMap(fset(process_map)).to_graph(), process_map.to_graph()
    )


def test_parallel_process_to_process_graph_nested() -> None:
    a = Process("A", 1)
    b = Process("B", 3)
    c = ParallelProcessMap(fset(a, b))
    e = Process("E", 5)
    s = ParallelProcessMap(fset(c, e))

    expected = ProcessGraph(
        edges=fset(
            Edge(0, 1, "A", 1),
            Edge(0, 1, "B", 3),
            Edge(0, 1, "E", 5),
        ),
        start=0,
        end=1,
    )
    result = s.to_graph()
    assert process_graphs_isomorphic(result, expected)
