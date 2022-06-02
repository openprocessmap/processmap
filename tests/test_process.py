from processmap import Edge, Union
from processmap import Process as P
from processmap import Graph, Series
from processmap.common import fset

from .common import isomorphic


class TestProcess:
    def test_to_graph(self) -> None:
        result = P("test", 1).to_graph()
        expected = Graph(edges=fset(Edge(5, 6, "test", 1)), start=5, end=6)
        assert isomorphic(result, expected)
        assert not isomorphic(
            result, Graph(edges=fset(Edge(5, 6, "test", 2)), start=5, end=6)
        )


class TestProcessMap:
    def test_add(self) -> None:
        embark = P("Embark", 1)
        sail = P("Sail", 2)
        result = embark + sail
        expected = Series(embark, sail)
        assert result == expected

    def test_or(self) -> None:
        unload = P("Unload", 1)
        refuel = P("Refuel", 2)
        result = unload | refuel
        expected = Union(unload, refuel)
        assert result == expected


class TestSerial:
    def test_nested(self) -> None:
        s = Series(
            Series(P("A", 1), P("B", 3)),
            P("E", 5),
        )
        expected = Graph(
            edges=fset(
                Edge(0, 1, "A", 1),
                Edge(1, 2, "B", 3),
                Edge(2, 3, "E", 5),
            ),
            start=0,
            end=3,
        )
        assert isomorphic(s.to_graph(), expected)


class TestUnion:
    def test_nested(self) -> None:
        s = Union(
            Union(P("A", 1), P("B", 3)),
            P("E", 5),
        )
        # TODO: do an actual union
        expected = Graph(
            edges=fset(
                Edge(0, 1, "A", 1),
                Edge(0, 1, "B", 3),
                Edge(0, 1, "E", 5),
            ),
            start=0,
            end=1,
        )
        assert isomorphic(s.to_graph(), expected)


#
# def test_process_with_resource() -> None:
#     quay = Resource()
#     dock = P("dock", 1).using(quay)
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
#             idle1 := P("idle", 0),
#             dock1 := P("dock ship 1", 1).using(quay),
#             idle2 := P("idle", 0),
#         )
#     )
#     dock2series = Series(
#         (
#             idle3 := P("idle", 0),
#             dock2 := P("dock ship 2", 1).using(quay),
#             idle4 := P("idle", 0),
#         )
#     )
#     dock_both = Union((dock1series, dock2series))
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
