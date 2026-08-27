from dataclasses import dataclass
from typing import Optional, Tuple, Callable, Dict
import networkx as nx
import numpy as np


def mutation_add_edge(G: nx.Graph) -> nx.Graph:
    return G

def mutation_remove_edge(G: nx.Graph) -> nx.Graph:
    return G

def mutation_add_vertex(G: nx.Graph) -> nx.Graph:
    return G

def mutation_remove_vertex(G: nx.Graph) -> nx.Graph:
    return G

def mutation_subdivision(G: nx.Graph) -> nx.Graph:
    return G

def mutation_contraction(G: nx.Graph) -> nx.Graph:
    return G

def mutation_replace_vertex_by_path(G: nx.Graph) -> nx.Graph:
    return G

def mutation_replace_vertex_by_star(G: nx.Graph) -> nx.Graph:
    return G

def mutation_replace_vertex_by_clique(G: nx.Graph) -> nx.Graph:
    return G

def mutation_replace_vertex_by_polyhedral(G: nx.Graph) -> nx.Graph:
    return G

def mutation_bipartition_neighborhood(G: nx.Graph) -> nx.Graph:
    return G

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


# @funsearch.run
def evaluate(current_size: int, min_size: int, max_size: int, score_fn: Callable) -> Optional[float]:
    print("[DEBUG] : Nous sommes dans la fonction evuluate()")

    G = solve(current_size)

    score = score_fn(G, min_size, max_size)

    return float(-score)


def solve(size: int, max_steps: int = 500) -> nx.Graph:
    G: nx.Graph = nx.empty_graph(size)
    step = 0

    while step < max_steps:
        priorities = []

        candidate_graphs: list[Optional[nx.Graph]] = []

        for mutation_name, mutation_function in MUTATION_REGISTRY.items():
            try:
                G_temp = mutation_function(G.copy())

                p = priority(G_temp, size)

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


# @funsearch.evolve
def priority(G: nx.Graph, current_size: int) -> float:
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

