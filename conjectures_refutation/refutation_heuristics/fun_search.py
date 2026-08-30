import importlib
import os
import sys
from dataclasses import dataclass
from operator import invert
from typing import Optional, Tuple, Callable, Dict, List, Any
import networkx as nx
import numpy as np
import conjectures_refutation.helpers.invariants as invariants

class DummyFunsearch:
    """Décorateurs factices pour satisfaire l'interpréteur Python."""
    @staticmethod
    def run(func):
        return func

    @staticmethod
    def evolve(func):
        return func

funsearch = DummyFunsearch()

def _get_next_node_id(G: nx.Graph, count: int = 1) -> list:
    """Retourne une liste d'identifiants uniques pour de nouveaux nœuds."""
    int_nodes = [n for n in G.nodes if isinstance(n, int)]
    base = max(int_nodes, default=-1) + 1
    return [base + i for i in range(count)]


def mutation_add_edge(G: nx.Graph) -> nx.Graph:
    """Ajoute la première arête manquante dans l'ordre lexicographique des paires."""
    H = G.copy()
    nodes = sorted(H.nodes())
    for i, u in enumerate(nodes):
        for v in nodes[i + 1 :]:
            if not H.has_edge(u, v):
                H.add_edge(u, v)
                return H
    return H


def mutation_remove_edge(G: nx.Graph) -> nx.Graph:
    """Supprime la première arête triée canoniquement."""
    H = G.copy()
    edges = sorted(tuple(sorted((u, v))) for u, v in H.edges())
    if edges:
        u, v = edges[0]
        H.remove_edge(u, v)
    return H


def mutation_add_vertex(G: nx.Graph) -> nx.Graph:
    """Ajoute un sommet et le relie au premier nœud existant."""
    H = G.copy()
    new_node = _get_next_node_id(H, 1)[0]
    H.add_node(new_node)
    nodes = sorted(G.nodes())
    if nodes:
        H.add_edge(new_node, nodes[0])
    return H


def mutation_remove_vertex(G: nx.Graph) -> nx.Graph:
    """Supprime le premier sommet dans l'ordre de tri."""
    H = G.copy()
    nodes = sorted(H.nodes())
    if nodes:
        H.remove_node(nodes[0])
    return H


def mutation_subdivision(G: nx.Graph) -> nx.Graph:
    """Subdivise la première arête en insérant un nouveau sommet au milieu."""
    H = G.copy()
    edges = sorted(tuple(sorted((u, v))) for u, v in H.edges())
    if edges:
        u, v = edges[0]
        new_node = _get_next_node_id(H, 1)[0]
        H.remove_edge(u, v)
        H.add_edge(u, new_node)
        H.add_edge(new_node, v)
    return H


def mutation_contraction(G: nx.Graph) -> nx.Graph:
    """Contracte la première arête (u, v) en fusionnant v dans u."""
    H = G.copy()
    edges = sorted(tuple(sorted((u, v))) for u, v in H.edges())
    if edges:
        u, v = edges[0]
        H = nx.contracted_nodes(H, u, v, self_loops=False)
    return H


def mutation_replace_vertex_by_path(G: nx.Graph) -> nx.Graph:
    """Remplace le premier sommet par un chemin P_k (où k = degré du sommet)."""
    H = G.copy()
    nodes = sorted(H.nodes())
    if not nodes:
        return H

    v = nodes[0]
    neighbors = sorted(H.neighbors(v))
    k = len(neighbors)

    if k == 0:
        return H

    new_nodes = _get_next_node_id(H, k)
    H.remove_node(v)

    for i in range(k - 1):
        H.add_edge(new_nodes[i], new_nodes[i + 1])

    for i, neighbor in enumerate(neighbors):
        H.add_edge(new_nodes[i], neighbor)

    return H


def mutation_replace_vertex_by_star(G: nx.Graph) -> nx.Graph:
    """Remplace le premier sommet par une étoile S_k connectée à ses voisins."""
    H = G.copy()
    nodes = sorted(H.nodes())
    if not nodes:
        return H

    v = nodes[0]
    neighbors = sorted(H.neighbors(v))
    k = len(neighbors)

    if k == 0:
        return H

    new_nodes = _get_next_node_id(H, k + 1)
    center = new_nodes[0]
    leaves = new_nodes[1:]

    H.remove_node(v)

    for leaf in leaves:
        H.add_edge(center, leaf)

    for leaf, neighbor in zip(leaves, neighbors):
        H.add_edge(leaf, neighbor)

    return H


def mutation_replace_vertex_by_clique(G: nx.Graph) -> nx.Graph:
    """Remplace le premier sommet par une clique K_k connectée à ses voisins."""
    H = G.copy()
    nodes = sorted(H.nodes())
    if not nodes:
        return H

    v = nodes[0]
    neighbors = sorted(H.neighbors(v))
    k = len(neighbors)

    if k == 0:
        return H

    new_nodes = _get_next_node_id(H, k)
    H.remove_node(v)

    for i in range(k):
        for j in range(i + 1, k):
            H.add_edge(new_nodes[i], new_nodes[j])

    for new_node, neighbor in zip(new_nodes, neighbors):
        H.add_edge(new_node, neighbor)

    return H


def mutation_replace_vertex_by_polyhedral(G: nx.Graph) -> nx.Graph:
    """Remplace le premier sommet par un tétraèdre (K4) et distribue les voisins de façon cyclique."""
    H = G.copy()
    nodes = sorted(H.nodes())
    if not nodes:
        return H

    v = nodes[0]
    neighbors = sorted(H.neighbors(v))
    new_nodes = _get_next_node_id(H, 4)

    H.remove_node(v)

    for i in range(4):
        for j in range(i + 1, 4):
            H.add_edge(new_nodes[i], new_nodes[j])

    for i, neighbor in enumerate(neighbors):
        target_node = new_nodes[i % 4]
        H.add_edge(target_node, neighbor)

    return H


def mutation_bipartition_neighborhood(G: nx.Graph) -> nx.Graph:
    """Scinde le premier sommet en deux (v1, v2) et répartit ses voisins selon la parité de leur index."""
    H = G.copy()
    nodes = sorted(H.nodes())
    if not nodes:
        return H

    v = nodes[0]
    neighbors = sorted(H.neighbors(v))
    v1, v2 = _get_next_node_id(H, 2)

    H.remove_node(v)
    H.add_edge(v1, v2)

    for i, neighbor in enumerate(neighbors):
        if i % 2 == 0:
            H.add_edge(v1, neighbor)
        else:
            H.add_edge(v2, neighbor)

    return H

FunSearchMutationFunction = Callable[[nx.Graph], nx.Graph]

MUTATION_REGISTRY: Dict[str, FunSearchMutationFunction] = {
    "add_edge": mutation_add_edge,
    "remove_edge": mutation_remove_edge,
    "add_vertex": mutation_add_vertex,
    "remove_vertex": mutation_remove_vertex,
    "subdivision": mutation_subdivision,
    "contraction": mutation_contraction,
    "replace_vertex_by_path": mutation_replace_vertex_by_path,
    "replace_vertex_by_star": mutation_replace_vertex_by_star,
    "replace_vertex_by_clique": mutation_replace_vertex_by_clique,
    "replace_vertex_by_polyhedral": mutation_replace_vertex_by_polyhedral,
    "bipartition_neighborhood": mutation_bipartition_neighborhood,
}


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


@funsearch.run
def evaluate(input_dict: dict) -> float:
    size = int(input_dict["size"])
    min_size = int(input_dict["min_size"])
    max_size = int(input_dict["max_size"])
    np_hard_invariants = bool(input_dict["np_hard_invariants"])
    score_function_path = str(input_dict["score_function_path"])
    score_function_name = str(input_dict["score_function_name"])

    actual_path = os.path.abspath(score_function_path)
    module_dir = os.path.dirname(actual_path)
    module_name = os.path.basename(actual_path)

    if module_name.endswith('.py'):
        module_name = module_name[:-3]

    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    custom_module = importlib.import_module(module_name)
    score_fn = getattr(custom_module, score_function_name)

    G = solve(size, np_hard_invariants)

    score = score_fn(G, min_size, max_size)

    return float(-score)


def solve(size: int, np_hard_invariants: bool, max_steps: int = 500) -> nx.Graph:
    G: nx.Graph = nx.empty_graph(size)
    step = 0

    while step < max_steps:
        priorities = []

        candidate_graphs: list[Optional[nx.Graph]] = []

        for mutation_name, mutation_function in MUTATION_REGISTRY.items():
            try:
                G_temp = mutation_function(G.copy())

                invariants = compute_invariants(G_temp, np_hard_invariants)

                p = priority(G_temp, size, invariants)

                priorities.append(p)
                candidate_graphs.append(G_temp)

            except Exception:
                priorities.append(float('-inf'))
                candidate_graphs.append(None)

        best_idx = int(np.argmax(priorities))

        if priorities[best_idx] == float('-inf'):
            break

        best_graph = candidate_graphs[best_idx]

        if best_graph is not None:
            G = best_graph

        step += 1

    return G


@funsearch.evolve
def priority(G: nx.Graph, current_size: int, invariants: Dict[str, float]) -> float:
    print("[DEBUG] : Nous sommes dans la fonction priority()")
    return 0


@dataclass(slots=True)
class FunSearchConfig:
    """Configuration parameters for the lightweight hill-climbing routine."""

    neighbour_count: int = 20
    min_size: int = 6
    max_size: int = 30
    max_mutations: int = 3
    time_limit: float = 60.0
    stagnation_limit: int = 10
    margin: float = 1e-3
    cache_size_limit: Optional[int] = None
    mutation_names: Optional[Tuple[str, ...]] = None
    verbose: bool = False
    seed: Optional[int] = None
    funsearch_llm_provider = None,
    funsearch_llm_temperature = None,
    funsearch_llm_max_tokens = None,
    subclass = None,


@dataclass(slots=True)
class FunSearchResult:
    """Outcome of a hill-climbing run against a single conjecture."""

    has_counterexample: bool
    counterexample_g6: str
    score: float
    x_value: Optional[float]
    y_value: Optional[float]
    time: float
    total_evaluated: int
    total_rejected: int
    reset: int

