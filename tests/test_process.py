from processmap import Edge, Graph
from processmap import Process as P
from processmap import Seq, Union
from processmap.common import fset

from .common import isomorphic


class TestProcess:
    def test_to_graph(self) -> None:
        result = P("test", 1).to_graph()
        expected = Graph(fset(Edge(5, 6, "test", 1)), start=fset(5), end=fset(6))
        assert isomorphic(result, expected)
        assert not isomorphic(
            result, Graph(fset(Edge(5, 6, "test", 2)), start=fset(5), end=fset(6))
        )


class TestSeq:
    def test_nested(self) -> None:
        s = Seq(
            Seq(P("A", 1), P("B", 3)),
            P("E", 5),
        )
        expected = Graph(
            fset(
                Edge(0, 1, "A", 1),
                Edge(1, 2, "<seq>", 0),
                Edge(2, 3, "B", 3),
                Edge(3, 4, "<seq>", 0),
                Edge(4, 5, "E", 5),
            ),
            start=fset(0),
            end=fset(5)
        )
        assert isomorphic(s, expected)


# class TestUnion:
#     def test_same_process(self) -> None:
#         p = P("A", 1)
#         assert isomorphic(p | p, p)

#     def test_different_process(self) -> None:
#         assert isomorphic(
#             P("A", 4) | P("B", 9),
#             Graph(
#                 fset(
#                     Edge(0, 1, "A", 4),
#                     Edge(2, 3, "B", 9),
#                 ),
#                 start=fset(0, 2),
#                 end=fset(1, 3),
#             ),
#         )

#     def test_process_overlaps_seq(self) -> None:
#         x = P("B", 1)
#         y = Seq(P("A", 1), Seq(x, P("C", 1)))
#         assert isomorphic(x | y, y)
#         assert isomorphic(y | x, y)

#     def test_process_doesnt_overlap_seq(self) -> None:
#         x = P("X", 1)
#         y = Seq(P("A", 1), Seq(P("B", 1), P("C", 1)))
#         assert isomorphic(
#             x | y,
#             expect := Graph(
#                 fset(
#                     Edge(0, 1, "A", 1),
#                     Edge(1, 2, "B", 1),
#                     Edge(2, 3, "C", 1),
#                     Edge(4, 5, "X", 1),
#                 ),
#                 start=fset(0, 4),
#                 end=fset(3, 5),
#             ),
#         )
#         assert isomorphic(y | x, expect)  # also in reverse order!

#     def test_seqs_without_overlap(self) -> None:
#         x = Seq(P("A", 1), Seq(P("B", 1), P("C", 1)))
#         y = Seq(P("D", 1), Seq(P("E", 1), P("F", 1)))
#         assert isomorphic(
#             x | y,
#             expect := Graph(
#                 fset(
#                     Edge(0, 1, "A", 1),
#                     Edge(1, 2, "B", 1),
#                     Edge(2, 3, "C", 1),
#                     Edge(4, 5, "D", 1),
#                     Edge(5, 6, "E", 1),
#                     Edge(6, 7, "F", 1),
#                 ),
#                 start=fset(0, 4),
#                 end=fset(3, 7),
#             ),
#         )
#         assert isomorphic(y | x, expect)  # also in reverse order!

    # def test_fully_disjoint_nested(self) -> None:
    #     assert isomorphic(
    #         union(P("A", 4), union(P("B", 9), P("C", 10))),
    #         Graph(
    #             fset(
    #                 Edge(0, 1, "A", 4),
    #                 Edge(2, 3, "B", 9),
    #                 Edge(4, 5, "C", 10),
    #             )
    #         ),
    #     )

    # def test_partially_disjoint(self) -> None:
    #     x = Seq(P("A", 1), Seq(b := P("B", 1), P("C", 1)))
    #     y = Seq(P("D", 1), Seq(b, P("E", 1)))
    #     assert isomorphic(
    #         union(x, y),
    #         Graph(
    #             fset(
    #                 Edge(0, 1, "A", 1),
    #                 Edge(4, 1, "D", 1),
    #                 Edge(1, 2, "B", 1),
    #                 Edge(2, 3, "C", 1),
    #                 Edge(2, 5, "E", 1),
    #             )
    #         ),
    #     )


class TestProcessMap:
    def test_add(self) -> None:
        embark = P("Embark", 1)
        sail = P("Sail", 2)
        result = embark + sail
        expected = Seq(embark, sail)
        assert result == expected


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
#     dock1series = Seq(
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
