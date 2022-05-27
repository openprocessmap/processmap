from processmap.helpers import fset
from processmap.process_graph import Edge, Node, ProcessGraph
from processmap.process_map import Process, SerialProcessMap, process


def test_process() -> None:
    assert process("test", 1, 2) == Process("test", 1, 2)


def test_process_default() -> None:
    assert process("test", 1) == Process("test", 1, 1)


def test_process_to_dag() -> None:
    assert process("test", 1, 2).to_dag() == ProcessGraph(
        end=Node(
            predecessors=fset(
                (
                    Edge(name="test", min_duration=1, max_duration=2),
                    Node(predecessors=frozenset()),
                )
            )
        )
    )


def test_serial_process_to_dag_from_processes() -> None:
    a = process("A", 1, 2)
    b = process("B", 3, 4)
    c = SerialProcessMap([a, b])
    d = process("D", 5, 6)
    s = SerialProcessMap([c, d])

    a1 = Node(predecessors=frozenset())
    a2 = Node(predecessors=fset((Edge("A", 1, 2), a1)))
    b2 = Node(predecessors=fset((Edge("B", 3, 4), a2)))
    d2 = Node(predecessors=fset((Edge("D", 5, 6), b2)))

    expected = ProcessGraph(end=d2)
    result = s.to_dag()

    assert result == expected
