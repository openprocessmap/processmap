from processmap.process_map import Edge, Node, Process, ProcessGraph, process


def test_process() -> None:
    assert process("test", 1, 2) == Process("test", 1, 2)


def test_process_default() -> None:
    assert process("test", 1) == Process("test", 1, 1)


def test_process_to_dag() -> None:
    assert process("test", 1, 2).to_dag() == ProcessGraph(
        end=Node(
            predecessors=frozenset(
                [
                    (
                        Edge(name="test", min_duration=1, max_duration=2),
                        Node(predecessors=frozenset()),
                    )
                ]
            )
        )
    )
