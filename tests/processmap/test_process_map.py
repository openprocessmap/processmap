from processmap.process_graph import EdgeInfo, ProcessGraph
from processmap.process_map import Process, SerialProcessMap, process
from tests.processmap.process_graph_equal import process_graphs_isomorphic


def test_process() -> None:
    assert process("test", 1, 2) == Process("test", 1, 2)


def test_process_default() -> None:
    assert process("test", 1) == Process("test", 1, 1)


def test_process_to_graph() -> None:
    p = process("test", 1, 2)
    result = p.to_graph()

    start = 100
    end = 101
    expected = ProcessGraph(
        edges={(start, end): EdgeInfo("test", 1, 2)}, first=100, last=101
    )
    assert process_graphs_isomorphic(result, expected)


def test_process_to_graph_unequal() -> None:
    p = process("test", 1, 2)
    result = p.to_graph()

    start = 100
    end = 101
    expected = ProcessGraph(
        edges={(start, end): EdgeInfo("test", 1, 3)}, first=100, last=101
    )

    assert not process_graphs_isomorphic(result, expected)


def test_serial_process_to_process_graph_empty() -> None:
    s = SerialProcessMap([])

    expected = ProcessGraph(
        edges={},
        first=0,
        last=0,
    )
    result = s.to_graph()

    assert process_graphs_isomorphic(result, expected)


def test_serial_process_to_process_graph_1() -> None:
    a = process("A", 1, 2)
    s = SerialProcessMap([a])

    expected = ProcessGraph(
        edges={
            (0, 1): EdgeInfo("A", 1, 2),
        },
        first=0,
        last=1,
    )
    result = s.to_graph()

    assert process_graphs_isomorphic(result, expected)


def test_serial_process_to_process_graph() -> None:
    a = process("A", 1, 2)
    b = process("B", 3, 4)
    c = SerialProcessMap([a, b])
    d = SerialProcessMap([])
    e = process("E", 5, 6)
    s = SerialProcessMap([c, d, e])

    expected = ProcessGraph(
        edges={
            (0, 1): EdgeInfo("A", 1, 2),
            (1, 2): EdgeInfo("B", 3, 4),
            (2, 3): EdgeInfo("E", 5, 6),
        },
        first=0,
        last=3,
    )
    result = s.to_graph()

    assert process_graphs_isomorphic(result, expected)
