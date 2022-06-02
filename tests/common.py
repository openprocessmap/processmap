from collections.abc import Mapping, Set

from networkx import MultiDiGraph, is_isomorphic  # type: ignore

from processmap import Graph, ProcessMap
from processmap.graph import Node


def _as_networkx(process_graph: Graph) -> MultiDiGraph:
    di_graph = MultiDiGraph()
    di_graph.add_nodes_from((node, node.attributes()) for node in process_graph.nodes)
    di_graph.add_edges_from(
        (edge.start, edge.end, edge.attributes()) for edge in process_graph.edges
    )
    return di_graph


def isomorphic_graph(_a: Graph | ProcessMap, _b: Graph | ProcessMap) -> bool:
    a: Graph = _a if isinstance(_a, Graph) else _a.to_graph()
    b: Graph = _b if isinstance(_b, Graph) else _b.to_graph()
    x = _as_networkx(a)
    y = _as_networkx(b)
    return (
        bool(is_isomorphic(x, y, node_match=Mapping.__eq__, edge_match=Mapping.__eq__))
        and _bounds(a) == (a.start, a.end)
        and _bounds(b) == (b.start, b.end)
    )


def _bounds(x: Graph) -> tuple[Set[Node], Set[Node]]:
    start = (x.nodes | {e.start for e in x.edges}) - {e.end for e in x.edges}
    end = (x.nodes | {e.end for e in x.edges}) - {e.start for e in x.edges}
    return start, end
