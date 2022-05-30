from collections.abc import Mapping

from networkx import DiGraph, is_isomorphic  # type: ignore

from processmap.process_graph import ProcessGraph, NodeId


def _make_digraph(process_graph: ProcessGraph) -> DiGraph:
    di_graph = DiGraph()
    di_graph.add_edges_from(
        (u, v, {"edge_info": edge_info})
        for (u, v), edge_info in process_graph.edges.items()
    )
    return di_graph


def process_graphs_isomorphic(a: ProcessGraph, b: ProcessGraph) -> bool:
    x = _make_digraph(a)
    y = _make_digraph(b)
    return (
        bool(is_isomorphic(x, y, edge_match=Mapping.__eq__))
        and _bounds(a) == (a.first, a.last)
        and _bounds(b) == (b.first, b.last)
    )


def _bounds(x: ProcessGraph) -> tuple[NodeId, NodeId]:
    if len(x.edges) == 0:
        return (x.first, x.first)
    # we can assume only one end/start exists
    [start] = {u for u, _ in x.edges} - {v for _, v in x.edges}
    [end] = {v for _, v in x.edges} - {u for u, _ in x.edges}
    return start, end
