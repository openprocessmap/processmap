import pytest

from processmap.helpers import fset
from processmap.process_graph import Edge, ProcessGraph
from processmap.process_map import Parallel, Process, ProcessMap, Series, space
from tests.processmap.process_graph_equal import process_graphs_isomorphic


@pytest.fixture
def process_map() -> ProcessMap:
    a = Process("A", 1)
    b = Process("B", 3)
    c = Series((a, b))
    e = Process("E", 5)
    return Series((c, e))


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
        Series(())


def test_serial_process_to_process_graph_1() -> None:
    a = Process("A", 1)
    s = Series((a,))

    expected = ProcessGraph(edges=fset(Edge(0, 1, "A", 1)), start=0, end=1)
    result = s.to_graph()
    assert process_graphs_isomorphic(result, expected)


def test_serial_process_to_process_graph() -> None:
    a = Process("A", 1)
    b = Process("B", 3)
    c = Series((a, b))
    e = Process("E", 5)
    s = Series((c, e))

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
        Parallel(())


def test_parallel_process_to_process_graph_single(process_map: ProcessMap) -> None:
    assert process_graphs_isomorphic(
        Parallel((process_map,)).to_graph(), process_map.to_graph()
    )


def test_parallel_process_to_process_graph_nested() -> None:
    a = Process("A", 1)
    b = Process("B", 3)
    c = Parallel((a, b))
    e = Process("E", 5)
    s = Parallel((c, e))

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


def test_process_map_add() -> None:
    embark = Process("Embark", 1)
    sail = Process("Sail", 2)
    disembark = Process("Disembark", 1)

    result = embark + sail + disembark

    expected = Series((embark, sail, disembark))

    assert result == expected


def test_process_map_or() -> None:
    unload = Process("Unload", 1)
    refuel = Process("Refuel", 2)

    result = unload | refuel

    expected = Parallel((space() + unload + space(), space() + refuel + space()))

    assert result == expected


#
# def test_process_with_resource() -> None:
#     quay = Resource()
#     dock = Process("dock", 1).using(quay)
#
#     result = dock.run(allocator=SimpleAllocator({quay: 1}))
#
#     expected = [
#         Start(dock, 0),
#         Request(dock, quay, 0),
#         Allocation(dock, quay, 0),
#         Release(dock, quay, 1),
#         End(dock, 1),
#     ]
#
#     assert result == expected
#
#
# def test_processes_with_conflicting_requests() -> None:
#     quay = object()
#     dock1series = Series(
#         (
#             idle1 := Process("idle", 0),
#             dock1 := Process("dock ship 1", 1).using(quay),
#             idle2 := Process("idle", 0),
#         )
#     )
#     dock2series = Series(
#         (
#             idle3 := Process("idle", 0),
#             dock2 := Process("dock ship 2", 1).using(quay),
#             idle4 := Process("idle", 0),
#         )
#     )
#     dock_both = Parallel((dock1series, dock2series))
#
#     result = list(dock_both.run())
#
#     expected = [
#         Start(dock_both, 0),
#         Start(dock1series, 0),
#         Start(idle1, 0),
#         End(idle1, 0),
#         Start(dock1, 0),
#         Request(dock1, quay, 0),
#         Start(dock2series, 0),
#         Start(idle3, 0),
#         End(idle3, 0),
#         Start(dock2, 0),
#         Request(dock2, quay, 0),
#         Allocation(dock1, quay, 0),
#         Release(dock1, quay, 1),
#         End(dock1, 1),
#         Start(idle2, 1),
#         End(idle2, 1),
#         End(dock1series, 1),
#         Allocation(dock2, quay, 1),
#         Release(dock2, quay, 2),
#         End(dock2, 2),
#         Start(idle4, 2),
#         End(idle4, 2),
#         End(dock2series, 2),
#         End(dock_both, 2),
#     ]
#
#     assert result == expected
