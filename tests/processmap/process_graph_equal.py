from collections.abc import Mapping

from networkx import DiGraph, is_isomorphic  # type: ignore

from processmap.process_graph import ProcessGraph


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
    return bool(is_isomorphic(x, y, edge_match=Mapping.__eq__))
