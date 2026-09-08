import networkx as nx


subclass_function = {
    "hamiltonian": build_hamiltonian_graph,
    "induced_subgraph": build_induced_subgraph,
    "bull_free": build_bull_free_graph,
    "paw_free": build_paw_free,
    "diamond_free": build_diamond_free_graph,
    "connected": build_connected_graph,
    "tree": build_tree_graph,
    "forest": build_forest_graph,
    "star": build_star_graph,
    "path": build_path_graph,
    "cycle": build_cycle_graph,
    "chordal": build_chordal_graph,
    "complete": build_complete_graph,
    "bipartite": build_bipartite_graph,
    "planar": build_planar_graph,
    "grid": build_grid_graph,
    "triangle_free": build_triangle_free_graph,
    "claw_free": build_claw_free_graph,
    "c4_free": build_c4_free_graph,
    "regular": build_regular_graph,
}

def build_graph(subclass: str, n: int) -> nx.Graph:
    if subclass not in subclass_function:
        raise ValueError(f"Sous-classe inconnue : '{subclass}'")

    func = subclass_function[subclass]

    return func(n)