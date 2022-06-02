from collections.abc import Mapping

from networkx import MultiDiGraph, is_isomorphic  # type: ignore

from processmap import NodeId, Graph


def _as_networkx(process_graph: Graph) -> MultiDiGraph:
    di_graph = MultiDiGraph()
    di_graph.add_edges_from(
        (edge.start, edge.end, {"name": edge.name, "duration": edge.duration})
        for edge in process_graph.edges
    )
    return di_graph


def isomorphic(a: Graph, b: Graph) -> bool:
    x = _as_networkx(a)
    y = _as_networkx(b)
    return (
        bool(is_isomorphic(x, y, edge_match=Mapping.__eq__))
        and _bounds(a) == (a.start, a.end)
        and _bounds(b) == (b.start, b.end)
    )


def _bounds(x: Graph) -> tuple[NodeId, NodeId]:
    if len(x.edges) == 0:  # TODO: remove?
        return (x.start, x.start)
    # We can assume only one end/start exists in a process graph
    [start] = {e.start for e in x.edges} - {e.end for e in x.edges}
    [end] = {e.end for e in x.edges} - {e.start for e in x.edges}
    return start, end
