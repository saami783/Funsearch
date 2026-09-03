import importlib
import os
import sys
from typing import Optional, Dict, Tuple
import networkx as nx
import numpy as np

from conjectures_refutation.refutation_heuristics.funsearch.helpers import dummy_funsearch as funsearch
from conjectures_refutation.refutation_heuristics.funsearch.helpers.funsearch_invariants import compute_invariants
from conjectures_refutation.refutation_heuristics.funsearch.helpers.funsearch_result import log_result
from conjectures_refutation.refutation_heuristics.funsearch.helpers.funsearch_mutations import MUTATION_REGISTRY


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

    G, total_mutations, total_graphs_generated = solve(size, np_hard_invariants)

    score = score_fn(G, min_size, max_size)

    log_result(G, score, total_mutations, total_graphs_generated, min_size, max_size)

    if score is None:
        return -10000.0

    return float(-score)


def solve(size: int, np_hard_invariants: bool, max_steps: int = 500) -> Tuple[nx.Graph, int, int]:
    G: nx.Graph = nx.empty_graph(size)
    step = 0

    total_mutations = 0
    total_graphs_generated = 1

    while step < max_steps:
        priorities = []

        candidate_graphs: list[Optional[nx.Graph]] = []

        for mutation_name, mutation_function in MUTATION_REGISTRY.items():
            total_mutations += 1
            try:
                G_temp = mutation_function(G.copy())
                total_graphs_generated += 1

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

    return G, total_mutations, total_graphs_generated


@funsearch.evolve
def priority(G: nx.Graph, current_size: int, invariants: Dict[str, float]) -> float:
  """
  Returns a priority score for the given graph `G`.

  This function is used to guide a local search algorithm. The goal is to mutate
  the graph to maximize a mathematical score function and find a counterexample
  to a graph theory conjecture.

  Args:
      G: The current NetworkX graph.
      current_size: The number of nodes in the graph.
      invariants: A dictionary containing pre-computed topological properties of the graph.
          Available keys include: "is_connected", "is_tree", "is_planar", "is_bipartite",
          "diameter", "radius", "maximum_degree", "average_degree", "density",
          "matching_number", "largest_eigenvalue", "triangle_number", "girth", etc.

  Return:
      A float representing the priority or "fitness" of the graph. Higher is better.
      Combine the values from the `invariants` dictionary using mathematical operations,
      non-linear combinations, or conditional logic (if/else) to invent a novel heuristic.
  """
  return 0

