from typing import Dict
import networkx as nx
import conjectures_refutation.helpers.invariants as invariants


def compute_invariants(G: nx.Graph, np_hard_invariants: bool) -> Dict[str, float]:
    """Calcule les propriétés topologiques pour guider le LLM."""

    list_invariants = {
        "is_connected": invariants.is_connected(G),
        "is_complete": invariants.is_complete(G),
        "is_tree": invariants.is_tree(G),
        "is_path": invariants.is_path(G),
        "is_star": invariants.is_star(G),
        "is_planar": invariants.is_planar(G),
        "is_chordal": invariants.is_chordal(G),
        "is_bipartite": invariants.is_bipartite(G),
        "is_triangle_free": invariants.triangle_number(G),
        "is_eulerian": invariants.is_eulerian(G),
        "is_hamiltonian": invariants.is_hamiltonian(G),
        "is_regular": invariants.is_regular(G),
        "contains_induced_subgraph": invariants.contains_induced_subgraph(G),
        "is_claw_free": invariants.is_claw_free(G),
        "is_bull_free": invariants.is_bull_free(G),
        "is_paw_free": invariants.is_paw_free(G),
        "is_diamond_free": invariants.is_diamond_free(G),
        "diameter": invariants.diameter(G),
        "radius": invariants.radius(G),
        "number_of_components": invariants.number_of_components(G),
        "largest_component_ratio": invariants.largest_component_ratio(G),
        "degree_variance": invariants.degree_variance(G),
        "average_clustering": invariants.average_clustering(G),
        "number_of_leaves": invariants.number_of_leaves(G),
        "number_of_articulation_points": invariants.number_of_articulation_points(G),
        "number_of_bridges": invariants.number_of_bridges(G),
        "girth": invariants.girth(G),
        "circumference": invariants.circumference(G),
        "size": invariants.size(G),
        "order": invariants.order(G),
        "max_degree": invariants.maximum_degree(G),
        "min_degree": invariants.minimum_degree(G),
        "avg_degree": invariants.average_degree(G),
        "density": invariants.density(G),
        "matching_number": invariants.matching_number(G),
        "spanning_tree_number": invariants.spanning_tree_number(G),
        "vertex_connectivity": invariants.vertex_connectivity(G),
        "edge_connectivity": invariants.edge_connectivity(G),
        "triangle_number": invariants.triangle_number(G),
        "proximity": invariants.proximity(G),
        "remoteness": invariants.remoteness(G),
        "harmonic_index": invariants.harmonic_index(G),
        "randic_index": invariants.randic_index(G),
        "modified_zagreb_2": invariants.modified_zagreb_2(G),
        "spectrum": invariants.spectrum(G),
        "largest_eigenvalue": invariants.largest_eigenvalue(G),
        "largest_distance_eigenvalue": invariants.largest_distance_eigenvalue(G),
        "connectivity": invariants.connectivity(G),
        "p_A": invariants.p_A(G),
        "p_D": invariants.p_D(G),
        "m": invariants.m(G)
    }

    if np_hard_invariants:
        list_invariants.update(
            {
                "treewidth": invariants.treewidth(G),
                "longest_path": invariants.longest_path(G),
                "longest_induced_path": invariants.longest_induced_path(G),
                "longest_induced_cycle": invariants.longest_induced_cycle(G),
                "chromatic_number": invariants.chromatic_number(G),
                "chromatic_index": invariants.chromatic_index(G),
                "clique_number": invariants.clique_number(G),
                "independence_number": invariants.independence_number(G),
                "vertex_cover_number": invariants.vertex_cover_number(G),
                "feedback_vertex_set_number": invariants.feedback_vertex_set_number(G),
                "domination_number": invariants.domination_number(G),
                "total_domination_number": invariants.total_domination_number(G),
                "independent_domination_number": invariants.independent_domination_number(G)
            }
        )

    return list_invariants