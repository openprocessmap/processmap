from processmap import DependencyEdge as DE
from processmap import Graph
from processmap import Process as P
from processmap import ProcessEdge as PE
from processmap import ProcessNode, Seq, Union
from processmap.common import fset
from processmap.graph import RequestNode, ReleaseNode
from processmap.process import Request

from .common import isomorphic_graph


class TestProcessMap:
    def test_rshift(self) -> None:
        embark = P("Embark", 1)
        sail = P("Sail", 2)
        result = embark >> sail
        expected = Seq(embark, sail)
        assert result == expected

    def test_or(self) -> None:
        fuel = P("Fuel", 1)
        load = P("Load", 2)
        result = fuel | load
        expected = Union(fuel, load)
        assert result == expected


class TestProcess:
    def test_identity_by_value(self) -> None:
        assert P("Sail", 1) == P("Sail", 1)

    def test_to_graph(self) -> None:
        result = P("test", 1).to_graph()
        expected = Graph(
            nodes=fset(x := ProcessNode(), y := ProcessNode()),
            edges=fset(PE(x, y, "test", 1)),
            start=fset(x),
            end=fset(y),
        )
        assert isomorphic_graph(result, expected)
        assert not isomorphic_graph(
            result,
            Graph(
                nodes=fset(x := ProcessNode(), y := ProcessNode()),
                edges=fset(PE(x, y, "test", 2)),
                start=fset(x),
                end=fset(y),
            ),
        )


class TestSeq:
    def test_nested(self) -> None:
        s = P("A", 1) >> P("B", 3) >> P("E", 5)
        expected = Graph(
            nodes=fset(
                a1 := ProcessNode(),
                a2 := ProcessNode(),
                b1 := ProcessNode(),
                b2 := ProcessNode(),
                c1 := ProcessNode(),
                c2 := ProcessNode(),
            ),
            edges=fset(
                PE(a1, a2, "A", 1),
                DE(a2, b1),
                PE(b1, b2, "B", 3),
                DE(b2, c1),
                PE(c1, c2, "E", 5),
            ),
            start=fset(a1),
            end=fset(c2),
        )
        assert isomorphic_graph(s, expected)


class TestUnion:
    def test_same_process(self) -> None:
        p = P("A", 1)
        assert isomorphic_graph(p | p, p)

    def test_different_process(self) -> None:
        assert isomorphic_graph(
            P("A", 4) | P("B", 9),
            Graph(
                nodes=fset(
                    a1 := ProcessNode(),
                    a2 := ProcessNode(),
                    b1 := ProcessNode(),
                    b2 := ProcessNode(),
                ),
                edges=fset(
                    PE(a1, a2, "A", 4),
                    PE(b1, b2, "B", 9),
                ),
                start=fset(a1, b1),
                end=fset(a2, b2),
            ),
        )

    def test_similar_process(self) -> None:
        assert isomorphic_graph(
            P("A", 1) | P("A", 1),
            Graph(
                nodes=fset(
                    x1 := ProcessNode(),
                    x2 := ProcessNode(),
                    y1 := ProcessNode(),
                    y2 := ProcessNode(),
                ),
                edges=fset(
                    PE(x1, x2, "A", 1),
                    PE(y1, y2, "A", 1),
                ),
                start=fset(x1, y1),
                end=fset(x2, y2),
            ),
        )

    def test_process_overlaps_seq(self) -> None:
        x = P("B", 1)
        y = P("A", 1) >> x >> P("C", 1)
        assert isomorphic_graph(x | y, y)
        assert isomorphic_graph(y | x, y)

    def test_process_doesnt_overlap_seq(self) -> None:
        x = P("X", 1)
        y = P("A", 1) >> P("B", 1) >> P("C", 1)
        expect = Graph(
            nodes=fset(
                x1 := ProcessNode(),
                x2 := ProcessNode(),
                a1 := ProcessNode(),
                a2 := ProcessNode(),
                b1 := ProcessNode(),
                b2 := ProcessNode(),
                c1 := ProcessNode(),
                c2 := ProcessNode(),
            ),
            edges=fset(
                PE(a1, a2, "A", 1),
                DE(a2, b1),
                PE(b1, b2, "B", 1),
                DE(b2, c1),
                PE(c1, c2, "C", 1),
                PE(x1, x2, "X", 1),
            ),
            start=fset(a1, x1),
            end=fset(c2, x2),
        )
        assert isomorphic_graph(x | y, expect)
        assert isomorphic_graph(y | x, expect)

    def test_seqs_without_overlap(self) -> None:
        x = P("A", 1) >> P("B", 1) >> P("C", 1)
        y = P("D", 1) >> P("E", 1) >> P("F", 1)
        assert isomorphic_graph(
            x | y,
            expect := Graph(
                nodes=fset(
                    a1 := ProcessNode(),
                    a2 := ProcessNode(),
                    b1 := ProcessNode(),
                    b2 := ProcessNode(),
                    c1 := ProcessNode(),
                    c2 := ProcessNode(),
                    d1 := ProcessNode(),
                    d2 := ProcessNode(),
                    e1 := ProcessNode(),
                    e2 := ProcessNode(),
                    f1 := ProcessNode(),
                    f2 := ProcessNode(),
                ),
                edges=fset(
                    PE(a1, a2, "A", 1),
                    DE(a2, b1),
                    PE(b1, b2, "B", 1),
                    DE(b2, c1),
                    PE(c1, c2, "C", 1),
                    PE(d1, d2, "D", 1),
                    DE(d2, e1),
                    PE(e1, e2, "E", 1),
                    DE(e2, f1),
                    PE(f1, f2, "F", 1),
                ),
                start=fset(a1, d1),
                end=fset(c2, f2),
            ),
        )
        assert isomorphic_graph(y | x, expect)  # also in reverse order!

    def test_fully_disjoint_nested(self) -> None:
        assert isomorphic_graph(
            P("A", 4) | P("B", 9) | P("C", 10),
            Graph(
                nodes=fset(
                    a1 := ProcessNode(),
                    a2 := ProcessNode(),
                    b1 := ProcessNode(),
                    b2 := ProcessNode(),
                    c1 := ProcessNode(),
                    c2 := ProcessNode(),
                ),
                edges=fset(
                    PE(a1, a2, "A", 4),
                    PE(b1, b2, "B", 9),
                    PE(c1, c2, "C", 10),
                ),
                start=fset(a1, b1, c1),
                end=fset(a2, b2, c2),
            ),
        )

    def test_partially_disjoint(self) -> None:
        x = P("A", 1) >> (b := P("B", 1)) >> P("C", 1)
        y = P("D", 1) >> b >> P("E", 1)
        expected = Graph(
            nodes=fset(
                a1 := ProcessNode(),
                a2 := ProcessNode(),
                b1 := ProcessNode(),
                b2 := ProcessNode(),
                c1 := ProcessNode(),
                c2 := ProcessNode(),
                d1 := ProcessNode(),
                d2 := ProcessNode(),
                e1 := ProcessNode(),
                e2 := ProcessNode(),
            ),
            edges=fset(
                PE(a1, a2, "A", 1),
                DE(a2, b1),
                PE(b1, b2, "B", 1),
                DE(b2, c1),
                PE(c1, c2, "C", 1),
                PE(d1, d2, "D", 1),
                DE(d2, b1),
                DE(b2, e1),
                PE(e1, e2, "E", 1),
            ),
            start=fset(a1, d1),
            end=fset(c2, e2),
        )
        assert isomorphic_graph(x | y, expected)
        assert isomorphic_graph(y | x, expected)


class TestRequest:
    def test_request(self) -> None:
        ship_required = Request(ship := object())
        expected = Graph(
                nodes=fset(node := RequestNode(requested_resource=ship)),
                edges=fset(),
                start=fset(node),
                end=fset(node),
            )

        assert isomorphic_graph(ship_required, expected)


class TestUsing:
    def test_using_single_process(self) -> None:
        sail_ship_with_crew = P("Sail", 1).using(ship := object(), crew := object())
        expected = Graph(
            nodes=fset(
                ship1 := RequestNode(requested_resource=ship),
                ship2 := ReleaseNode(released_resource=ship),
                crew1 := RequestNode(requested_resource=crew),
                crew2 := ReleaseNode(released_resource=crew),
                sail1 := ProcessNode(),
                sail2 := ProcessNode(),
            ),
            edges=fset(
                DE(ship1, sail1),
                DE(crew1, sail1),
                PE(sail1, sail2, "Sail", 1),
                DE(sail2, crew2),
                DE(sail2, ship2),
            ),
            start=fset(ship1, crew1),
            end=fset(crew2, ship2),
        )

        result = sail_ship_with_crew.to_graph()

        assert isomorphic_graph(result, expected)



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
