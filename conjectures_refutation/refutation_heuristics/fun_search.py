from dataclasses import dataclass
from random import randint
from typing import Optional, Tuple, Callable
import networkx as nx

from conjectures_refutation.helpers.utility import MUTATION_REGISTRY, generate_init_graph


# @funsearch.run
def evaluate(min_size: int, max_size: int, score_fn: Callable) -> Optional[float]:
    print("[DEBUG] : Nous sommes dans la fonction evuluate()")

    G = solve(min_size, max_size)

    score = score_fn(G, min_size, max_size)

    return float(score)


def solve(min_size: int, max_size: int, graphs_per_mutation: int | None = None, num_steps: int = 100) -> nx.Graph:
    print("[DEBUG] : Nous sommes dans la fonction solve()")
    G = generate_init_graph(min_size, max_size)

    if graphs_per_mutation is None:
        graphs_per_mutation = randint(min_size, max_size)

    for step in range(num_steps):
        best_candidate = None
        best_score = float('-inf')

        for mut_name, mut_func in MUTATION_REGISTRY.items():
            print(f"Application de la mutation {mut_name}")
            for _ in range(graphs_per_mutation):
                try:
                    g_mutated = mut_func(G)

                    n_nodes = g_mutated.number_of_nodes()
                    if n_nodes < min_size or n_nodes > max_size:
                        continue

                    score = priority(g_mutated)

                    if score > best_score:
                        best_score = score
                        best_candidate = g_mutated

                except Exception:
                    continue

        if best_candidate is not None:
            G = best_candidate
        else:
            break

    return G


# @funsearch.evolve
def priority(G: nx.Graph) -> float:
    print("[DEBUG] : Nous sommes dans la fonction priority()")
    return float(G.number_of_edges())


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

