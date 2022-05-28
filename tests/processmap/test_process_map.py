from processmap.helpers import fset
from processmap.process_graph import Edge, Node, ProcessGraph
from processmap.process_map import Process, SerialProcessMap, process


def test_process() -> None:
    assert process("test", 1, 2) == Process("test", 1, 2)


def test_process_default() -> None:
    assert process("test", 1) == Process("test", 1, 1)


def test_process_to_dag() -> None:
    result = process("test", 1, 2).to_dag()
    expected = ProcessGraph(edges=fset(Edge(Node(), Node(), "test", 1, 2)))

    assert result == expected


def test_serial_process_to_dag() -> None:
    a = process("A", 1, 2)
    b = process("B", 3, 4)
    c = SerialProcessMap([a, b])
    d = process("D", 5, 6)
    s = SerialProcessMap([c, d])

    a1 = Node()
    a2 = Node()
    b2 = Node()
    d2 = Node()

    expected = ProcessGraph(
        fset(
            Edge(a1, a2, "A", 1, 2),
            Edge(a2, b2, "B", 3, 4),
            Edge(b2, d2, "D", 5, 6),
        )
    )
    result = s.to_dag()

    assert result == expected
