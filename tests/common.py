from collections.abc import Mapping, Set

from networkx import MultiDiGraph, is_isomorphic  # type: ignore

from processmap import Graph, NodeId, ProcessMap


def _as_networkx(process_graph: Graph) -> MultiDiGraph:
    di_graph = MultiDiGraph()
    di_graph.add_edges_from(
        (edge.start, edge.end, {"name": edge.name, "duration": edge.duration})
        for edge in process_graph.edges
    )
    return di_graph


# TODO: rename to make clear no process graph isomorphism
def isomorphic(_a: Graph | ProcessMap, _b: Graph | ProcessMap) -> bool:
    a: Graph = _a if isinstance(_a, Graph) else _a.to_graph()
    b: Graph = _b if isinstance(_b, Graph) else _b.to_graph()
    x = _as_networkx(a)
    y = _as_networkx(b)
    return (
        bool(is_isomorphic(x, y, edge_match=Mapping.__eq__))
        and _bounds(a) == (a.start, a.end)
        and _bounds(b) == (b.start, b.end)
    )


def _bounds(x: Graph) -> tuple[Set[NodeId], Set[NodeId]]:
    start = {e.start for e in x.edges} - {e.end for e in x.edges}
    end = {e.end for e in x.edges} - {e.start for e in x.edges}
    return start, end
