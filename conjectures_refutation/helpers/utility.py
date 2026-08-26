"""Utility helpers for conjecture loading, evaluation, and graph mutations."""

from __future__ import annotations

import ast
import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import networkx as nx
import numpy as np

from .invariants import binary_properties_functions, invariants_functions

Graph = nx.Graph
ConjectureRow = Dict[str, Any]
_RANDOM_RANGE = 2 ** 32


def _next_seed() -> int:
    """Return a deterministic 32-bit seed derived from the global RNG."""

    return random.randrange(_RANDOM_RANGE)


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------


def load_conjectures(
    csv_path: str | Path,
    *,
    as_dataclasses: bool = False,
) -> List[ConjectureRow] | List["Conjecture"]:
    """Load conjectures from ``csv_path``.

    By default the function mirrors the historical behaviour and returns raw
    dictionaries.  When ``as_dataclasses`` is ``True`` the records are converted
    into :class:`Conjecture` instances for stronger typing.
    """

    path = Path(csv_path)
    rows: List[ConjectureRow] = []

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            mutable = dict(row)
            coefficients_text = mutable.get("coefficients", "")
            try:
                mutable["coefficients"] = list(ast.literal_eval(coefficients_text))
            except (SyntaxError, ValueError, TypeError):
                print(
                    "Unable to parse coefficients for conjecture",
                    mutable.get("ID", "<unknown>"),
                )
                continue
            try:
                mutable["degree"] = int(mutable.get("degree", 0))
            except (TypeError, ValueError):
                mutable["degree"] = 0
            rows.append(mutable)

    if as_dataclasses:
        return [Conjecture.from_row(row) for row in rows]
    return rows


# ---------------------------------------------------------------------------
# Structured representation of conjectures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Conjecture:
    """Structured representation of a benchmark conjecture."""

    identifier: str
    statement: str
    subclass: str
    x_invariant: str
    y_invariant: str
    bound_type: str
    coefficients: Tuple[float, ...]
    degree: int
    counterexample_g6: Optional[str] = None
    x_value: Optional[float] = None
    y_value: Optional[float] = None
    order: Optional[float] = None
    counterexample_source: Optional[str] = None

    @classmethod
    def from_row(cls, row: ConjectureRow) -> "Conjecture":
        coefficients = tuple(float(value) for value in row.get("coefficients", []))
        degree = int(row.get("degree", 0))
        bound_type = (row.get("bound_type") or "upper").strip().lower()
        if bound_type not in {"upper", "lower"}:
            raise ValueError(f"Unsupported bound type: {bound_type!r}")
        return cls(
            identifier=str(row.get("ID", "")).strip(),
            statement=row.get("conjecture", ""),
            subclass=(row.get("subclass") or "").strip(),
            x_invariant=(row.get("x_invariant") or "").strip(),
            y_invariant=(row.get("y_invariant") or "").strip(),
            bound_type=bound_type,
            coefficients=coefficients,
            degree=degree,
            counterexample_g6=row.get("counterexample_g6") or None,
            x_value=_safe_float(row.get("x_value")),
            y_value=_safe_float(row.get("y_value")),
            order=_safe_float(row.get("order")),
            counterexample_source=row.get("counterexample_source") or None,
        )


def _safe_float(value: Optional[str]) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Invariants and quick eligibility checks
# ---------------------------------------------------------------------------


def _lookup_invariant(name: str) -> callable:
    try:
        return invariants_functions[name]
    except KeyError as exc:
        raise KeyError(f"Unknown invariant '{name}'") from exc


def compute_x_val_conjecture(graph: Graph, conjecture: ConjectureRow) -> float:
    """Return the value of the invariant selected by ``x_invariant``."""

    invariant = _lookup_invariant(conjecture["x_invariant"])
    return invariant(graph)


def compute_y_val_conjecture(graph: Graph, conjecture: ConjectureRow) -> float:
    """Return the value of the invariant selected by ``y_invariant``."""

    invariant = _lookup_invariant(conjecture["y_invariant"])
    return invariant(graph)


def evaluate_polynomial(x_value: float, coefficients: Sequence[float]) -> float:
    """Return ``sum(coefficients[i] * x_value ** i)``."""

    return sum(coeff * (x_value ** idx) for idx, coeff in enumerate(coefficients))


def check_subclasses(graph: Graph, subclass_text: str | None) -> bool:
    """Validate that ``graph`` satisfies every subclass predicate.

    ``subclass_text`` may contain several properties separated by commas.  An
    empty string (or ``None``) is treated as "no constraint" and yields ``True``.
    ``binary_properties_functions`` supplies the predicate implementations.
    """

    if not subclass_text:
        return True

    for token in (item.strip() for item in subclass_text.split(",")):
        if not token:
            continue
        try:
            predicate = binary_properties_functions[token]
        except KeyError as exc:
            raise KeyError(f"Unknown subclass predicate '{token}'") from exc
        if not predicate(graph):
            return False
    return True


def get_invariants(
    graph: Graph,
    conjecture: ConjectureRow,
    min_size: int,
    max_size: int,
) -> Optional[Tuple[float, float]]:
    """Return ``(x, y)`` when ``graph`` is eligible for ``conjecture``.

    Eligibility requires:
    * ``graph`` order within ``[min_size, max_size]``
    * satisfaction of subclass predicates
    * ability to evaluate the x/y invariants
    """

    if graph.number_of_nodes() < min_size or graph.number_of_nodes() > max_size:
        return None
    if not check_subclasses(graph, conjecture.get("subclass")):
        return None
    x_value = compute_x_val_conjecture(graph, conjecture)
    y_value = compute_y_val_conjecture(graph, conjecture)
    if x_value is None or y_value is None:
        return None
    return x_value, y_value


def evaluation(x_value: float, y_value: float, conjecture: ConjectureRow) -> float:
    """Return the signed score for ``conjecture`` evaluated at ``(x_value, y_value)``."""

    polynomial_value = evaluate_polynomial(x_value, conjecture["coefficients"])
    if conjecture["bound_type"] == "upper":
        return polynomial_value - y_value
    return y_value - polynomial_value


def order_within_bounds(graph: Graph, min_size: Optional[int], max_size: Optional[int]) -> bool:
    """Return ``True`` when ``graph`` has an order compatible with the bounds."""

    order = graph.number_of_nodes()
    if min_size is not None and order < min_size:
        return False
    if max_size is not None and order > max_size:
        return False
    return True


@dataclass(frozen=True)
class ConjectureResult:
    """Outcome of testing a graph against a conjecture."""

    conjecture: Conjecture
    x_value: float
    y_value: float
    polynomial_value: float
    score: float
    margin: float = 0.0

    @property
    def is_counterexample(self) -> bool:
        return self.score < -self.margin


def evaluate_conjecture(
    graph: Graph,
    conjecture: Conjecture,
    *,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    ensure_subclass: bool = True,
    margin: float = 0.0,
) -> Optional[ConjectureResult]:
    """Evaluate ``conjecture`` on ``graph`` and return a structured result."""

    if ensure_subclass and not check_subclasses(graph, conjecture.subclass):
        return None
    if not order_within_bounds(graph, min_size, max_size):
        return None

    x_value = compute_x_value(graph, conjecture)
    y_value = compute_y_value(graph, conjecture)
    polynomial_value = evaluate_polynomial(x_value, conjecture.coefficients)

    if conjecture.bound_type == "upper":
        score = polynomial_value - y_value
    else:
        score = y_value - polynomial_value

    return ConjectureResult(
        conjecture=conjecture,
        x_value=x_value,
        y_value=y_value,
        polynomial_value=polynomial_value,
        score=score,
        margin=margin,
    )


def compute_x_value(graph: Graph, conjecture: Conjecture) -> float:
    return _lookup_invariant(conjecture.x_invariant)(graph)


def compute_y_value(graph: Graph, conjecture: Conjecture) -> float:
    return _lookup_invariant(conjecture.y_invariant)(graph)


def test_conjecture_on_graph(
    graph: Graph,
    conjecture: Conjecture,
    *,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    ensure_subclass: bool = True,
    margin: float = 0.0,
) -> Optional[ConjectureResult]:
    """Convenience helper printing a textual summary of the evaluation."""

    result = evaluate_conjecture(
        graph,
        conjecture,
        min_size=min_size,
        max_size=max_size,
        ensure_subclass=ensure_subclass,
        margin=margin,
    )

    if result is None:
        print("Graph does not satisfy the eligibility conditions for this conjecture.")
        return None

    inequality = "y(G) <= P(x)" if conjecture.bound_type == "upper" else "y(G) >= P(x)"
    print(f"Conjecture {result.conjecture.identifier} score: {result.score:.6f}")
    print(f"Expected inequality: {inequality}")
    print(
        f"x = {result.x_value:.6f}, y = {result.y_value:.6f}, "
        f"P(x) = {result.polynomial_value:.6f}"
    )
    if result.is_counterexample:
        print("Result: counterexample detected.")
    else:
        print("Result: conjecture holds for this graph.")
    return result


# ---------------------------------------------------------------------------
# Graph manipulation
# ---------------------------------------------------------------------------


def repair_graph(graph: Graph) -> Graph:
    """Return a connected graph derived from ``graph``.

    When ``graph`` is disconnected, only the largest connected component is
    retained.  The behaviour matches the original helper while making the intent
    explicit.
    """

    if nx.is_connected(graph):
        return graph
    largest_cc = max(nx.connected_components(graph), key=len)
    return graph.subgraph(largest_cc).copy()


# ---------------------------------------------------------------------------
# Random graph generation
# ---------------------------------------------------------------------------


def generate_init_graph(min_size: int, max_size: int) -> Graph:
    """Return a random graph with order in ``[min_size, max_size]``.

    The distribution mirrors the historical implementation: a graph family is
    picked uniformly from a curated list, then a random instance of that family
    is sampled.
    """

    size = random.randint(min_size, max_size)
    generators = {
        "random": lambda: generate_random_graph(size, p=random.random(), seed=_next_seed()),
        "tree": lambda: nx.random_labeled_tree(size, seed=_next_seed()),
        "star": lambda: nx.star_graph(size - 1),
        "path": lambda: nx.path_graph(size),
        "cycle": lambda: nx.cycle_graph(size),
        "clique": lambda: nx.complete_graph(size),
        "bipartite": lambda: generate_bipartite_connected_graph(size, p=random.random(), seed=_next_seed()),
        "planar": lambda: generate_random_platonic_graph(seed=_next_seed()),
        "regular": lambda: _safe_random_regular_graph(size, seed=_next_seed()),
    }
    choice = random.choice(list(generators))
    return generators[choice]()


def _safe_random_regular_graph(size: int, *, seed: Optional[int] = None) -> Graph:
    """Return a (simple) 3-regular graph.

    3-regular requires n·3 to be even, so n must be even and n ≥ 4.
    Adjusts ``size`` down to the nearest even integer ≥ 4 when needed.
    """
    seed = seed if seed is not None else _next_seed()
    # ensure n is even and at least 4
    n = size if size % 2 == 0 else size - 1
    n = max(4, n)
    try:
        return nx.random_regular_graph(3, n, seed=seed)
    except nx.NetworkXError:
        return nx.random_regular_graph(3, max(4, n - 2), seed=seed)


def generate_init_graph_v2(min_size: int, max_size: int) -> Graph:
    """Legacy variant kept for backwards compatibility with notebooks."""

    size = random.randint(min_size, max_size)
    generators = {
        "random": lambda: generate_random_graph(size, p=random.random(), seed=_next_seed()),
        "tree": lambda: nx.random_labeled_tree(size, seed=_next_seed()),
        "star": lambda: nx.star_graph(size - 1),
        "path": lambda: nx.path_graph(size),
        "cycle": lambda: nx.cycle_graph(size),
        "clique": lambda: nx.complete_graph(size),
        "bipartite": lambda: generate_bipartite_connected_graph(size, p=random.random(), seed=_next_seed()),
        "planar": lambda: generate_random_platonic_graph(seed=_next_seed()),
    }
    choice = random.choice(list(generators))
    graph = generators[choice]()
    fresh_labels = random.sample(range(max_size), graph.number_of_nodes())
    mapping = {old: new for old, new in zip(graph.nodes(), fresh_labels)}
    return nx.relabel_nodes(graph, mapping)


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------


def _new_node_label(graph: nx.Graph) -> int:
    """Return an integer label that does not exist in ``graph``."""

    return (max(graph.nodes, default=-1) + 1) if graph.nodes else 0


def _copy_graph(graph: nx.Graph) -> nx.Graph:
    return graph.copy()


def mutation_add_edge(graph: nx.Graph) -> nx.Graph:
    """Add an edge between two non-adjacent vertices or create a new leaf."""

    mutated = _copy_graph(graph)
    non_edges = sorted(nx.non_edges(mutated))
    if non_edges:
        u, v = random.choice(non_edges)
        mutated.add_edge(u, v)
        return mutated
    return mutation_add_vertex(mutated)


def mutation_remove_edge(graph: nx.Graph) -> nx.Graph:
    """Remove an edge without breaking connectivity."""

    mutated = _copy_graph(graph)
    edges = sorted(mutated.edges())
    random.shuffle(edges)
    for u, v in edges:
        mutated.remove_edge(u, v)
        if nx.is_connected(mutated):
            return mutated
        mutated.add_edge(u, v)
    return _copy_graph(graph)


def mutation_add_vertex(graph: nx.Graph) -> nx.Graph:
    """Attach a fresh vertex to exactly one random existing vertex (if any)."""

    mutated = _copy_graph(graph)
    new_node = _new_node_label(mutated)
    mutated.add_node(new_node)
    if mutated.number_of_nodes() == 1:
        return mutated
    candidates = sorted(n for n in mutated.nodes if n != new_node)
    u = random.choice(candidates)
    mutated.add_edge(new_node, u)
    return mutated


def mutation_remove_vertex(graph: nx.Graph) -> nx.Graph:
    """Remove a non-articulation vertex if possible."""

    if graph.number_of_nodes() <= 1:
        return _copy_graph(graph)
    mutated = _copy_graph(graph)
    articulation_points = set(nx.articulation_points(mutated))
    removable = sorted(set(mutated.nodes()) - articulation_points)
    if not removable:
        return _copy_graph(graph)
    mutated.remove_node(random.choice(removable))
    return nx.convert_node_labels_to_integers(mutated, ordering="default")


def mutation_subdivision(graph: nx.Graph) -> nx.Graph:
    """Subdivide a random edge by inserting a fresh vertex."""

    if graph.number_of_edges() == 0:
        return _copy_graph(graph)
    mutated = _copy_graph(graph)
    u, v = random.choice(sorted(mutated.edges()))
    new_node = _new_node_label(mutated)
    mutated.remove_edge(u, v)
    mutated.add_node(new_node)
    mutated.add_edge(u, new_node)
    mutated.add_edge(new_node, v)
    return mutated


def mutation_contraction(graph: nx.Graph) -> nx.Graph:
    """Contract a random edge while keeping the graph simple."""

    if graph.number_of_edges() == 0:
        return _copy_graph(graph)
    G = _copy_graph(graph)
    u, v = random.choice(sorted(G.edges()))
    neighbours = sorted((set(G.neighbors(u)) | set(G.neighbors(v))) - {u, v})
    if G.has_node(u):
        G.remove_node(u)
    if G.has_node(v):
        G.remove_node(v)
    merged = _new_node_label(G)
    G.add_node(merged)
    for nbr in neighbours:
        G.add_edge(merged, nbr)
    return nx.convert_node_labels_to_integers(nx.Graph(G), ordering="default")


def mutation_replace_vertex_by_path(graph: nx.Graph) -> nx.Graph:
    """Replace a vertex by a path and reconnect neighbours to the midpoint."""

    if graph.number_of_nodes() == 0:
        return _copy_graph(graph)
    mutated = _copy_graph(graph)
    vertex = random.choice(sorted(mutated.nodes()))
    neighbours = sorted(mutated.neighbors(vertex))
    mutated.remove_node(vertex)
    path_length = random.randint(3, 10)
    mutated.add_node(vertex)
    path_nodes = [vertex]
    next_label = _new_node_label(mutated)
    for _ in range(path_length - 1):
        label = next_label
        mutated.add_node(label)
        path_nodes.append(label)
        next_label += 1
    for i in range(len(path_nodes) - 1):
        mutated.add_edge(path_nodes[i], path_nodes[i + 1])
    midpoint = path_nodes[len(path_nodes) // 2]
    for nb in neighbours:
        if nb != midpoint:
            mutated.add_edge(nb, midpoint)
    return mutated


def mutation_replace_vertex_by_star(graph: nx.Graph) -> nx.Graph:
    """Replace a vertex by a star whose centre assumes its role."""

    if graph.number_of_nodes() == 0:
        return _copy_graph(graph)
    mutated = _copy_graph(graph)
    vertex = random.choice(sorted(mutated.nodes()))
    neighbours = sorted(mutated.neighbors(vertex))
    mutated.remove_node(vertex)
    centre = vertex
    mutated.add_node(centre)
    star_size = random.randint(3, 10)
    leaf_count = max(0, star_size - 1)
    next_label = _new_node_label(mutated)
    for _ in range(leaf_count):
        leaf = next_label
        next_label += 1
        mutated.add_node(leaf)
        mutated.add_edge(centre, leaf)
    for nb in neighbours:
        mutated.add_edge(nb, centre)
    return mutated


def mutation_replace_vertex_by_clique(graph: nx.Graph) -> nx.Graph:
    """Replace a vertex by a clique and reconnect neighbours randomly."""

    if graph.number_of_nodes() == 0:
        return _copy_graph(graph)
    mutated = _copy_graph(graph)
    vertex = random.choice(sorted(mutated.nodes()))
    neighbours = sorted(mutated.neighbors(vertex))
    mutated.remove_node(vertex)
    clique_size = random.randint(3, 10)
    clique_nodes = [vertex]
    mutated.add_node(vertex)
    next_label = _new_node_label(mutated)
    for _ in range(1, clique_size):
        clique_nodes.append(next_label)
        mutated.add_node(next_label)
        next_label += 1
    for i, u in enumerate(clique_nodes):
        for v in clique_nodes[i + 1:]:
            mutated.add_edge(u, v)
    for nb in neighbours:
        mutated.add_edge(nb, vertex)
    return mutated


def mutation_replace_vertex_by_polyhedral(graph: nx.Graph) -> nx.Graph:
    """Replace a vertex by a small Platonic solid subgraph."""

    if graph.number_of_nodes() == 0:
        return _copy_graph(graph)
    mutated = _copy_graph(graph)
    vertex = random.choice(sorted(mutated.nodes()))
    neighbours = sorted(mutated.neighbors(vertex))
    mutated.remove_node(vertex)
    mutated.add_node(vertex)
    solids = [
        nx.tetrahedral_graph(),
        nx.cubical_graph(),
        nx.octahedral_graph(),
        nx.icosahedral_graph(),
    ]
    solid = random.choice(solids)
    mapping = {}
    nodes = sorted(solid.nodes())
    mapping[nodes[0]] = vertex
    next_label = _new_node_label(mutated)
    for node in nodes[1:]:
        label = next_label
        mapping[node] = label
        mutated.add_node(label)
        next_label += 1
    for u, v in sorted(solid.edges()):
        if mapping[u] != mapping[v]:
            mutated.add_edge(mapping[u], mapping[v])
    for neighbour in neighbours:
        mutated.add_edge(vertex, neighbour)
    return mutated


def mutation_bipartition_neighborhood(graph: nx.Graph) -> nx.Graph:
    """Rewire the neighborhood of a vertex according to a random bipartition."""

    if graph.number_of_nodes() == 0:
        return _copy_graph(graph)
    G = _copy_graph(graph)
    u = random.choice(sorted(G.nodes()))
    neighbours = sorted(G.neighbors(u))
    if len(neighbours) < 2:
        return G
    G.remove_node(u)
    random.shuffle(neighbours)
    split = max(1, len(neighbours) // 2)
    part1 = neighbours[:split]
    part2 = neighbours[split:]
    if not part2:
        part2 = [part1.pop()]
    u1 = _new_node_label(G)
    G.add_node(u1)
    u2 = _new_node_label(G)
    G.add_node(u2)
    G.add_edge(u1, u2)
    for v in part1:
        G.add_edge(u1, v)
    for v in part2:
        G.add_edge(u2, v)
    for v in part1:
        for w in part2:
            if not G.has_edge(v, w):
                G.add_edge(v, w)
    return G


def mutation_double_edge_swap(graph: nx.Graph) -> nx.Graph:
    """Swap two independent edges {a,b},{c,d} -> {a,c},{b,d} (degrees preserved).

    Mutation clé pour les sous-classes rigides (graphes réguliers) : la séquence
    de degrés est invariante, donc un voisin d'un graphe régulier reste régulier.
    On rejette les swaps qui déconnectent le graphe.
    """

    mutated = _copy_graph(graph)
    edges = sorted(mutated.edges())
    if len(edges) < 2:
        return mutated
    for _ in range(30):  # tentatives
        (a, b), (c, d) = random.sample(edges, 2)
        if len({a, b, c, d}) < 4:
            continue
        if mutated.has_edge(a, c) or mutated.has_edge(b, d):
            continue
        mutated.remove_edge(a, b)
        mutated.remove_edge(c, d)
        mutated.add_edge(a, c)
        mutated.add_edge(b, d)
        if nx.is_connected(mutated):
            return mutated
        # annule et retente
        mutated.remove_edge(a, c)
        mutated.remove_edge(b, d)
        mutated.add_edge(a, b)
        mutated.add_edge(c, d)
    return mutated


def mutation_leaf_relocate(graph: nx.Graph) -> nx.Graph:
    """Détache une feuille et la rattache à un autre sommet (préserve les arbres).

    Sur un arbre, le résultat est toujours un arbre : mutation adaptée aux
    conjectures restreintes aux arbres (Shor, domination exponentielle...).
    Sur un graphe quelconque, déplace un sommet de degré 1 si possible.
    """

    mutated = _copy_graph(graph)
    leaves = sorted(v for v, d in mutated.degree() if d == 1)
    if not leaves:
        return mutated
    leaf = random.choice(leaves)
    parent = next(iter(mutated.neighbors(leaf)))
    candidates = sorted(v for v in mutated.nodes() if v not in (leaf, parent))
    if not candidates:
        return mutated
    new_parent = random.choice(candidates)
    mutated.remove_edge(leaf, parent)
    mutated.add_edge(leaf, new_parent)
    return mutated


# ---------------------------------------------------------------------------
# Additional random generators (ported from the legacy module)
# ---------------------------------------------------------------------------


def generate_bipartite_connected_graph(
    size: int,
    p: float = 0.5,
    *,
    seed: Optional[int] = None,
) -> Graph:
    """Return a connected random bipartite graph with ``size`` vertices."""

    left_size = size // 2
    right_size = size - left_size
    graph = nx.Graph()
    left = [f"L{i}" for i in range(left_size)]
    right = [f"R{i}" for i in range(right_size)]
    graph.add_nodes_from(left, bipartite=0)
    graph.add_nodes_from(right, bipartite=1)
    rng = random.Random(seed)
    for u in left:
        for v in right:
            if rng.random() < p:
                graph.add_edge(u, v)
    if not graph.edges:
        graph.add_edge(rng.choice(left), rng.choice(right))
    if not nx.is_connected(graph):
        graph = repair_graph(graph)
    return nx.convert_node_labels_to_integers(graph, ordering="default")


def generate_random_platonic_graph(*, seed: Optional[int] = None) -> Graph:
    """Return a random Platonic solid graph."""

    solids = [
        nx.tetrahedral_graph(),
        nx.cubical_graph(),
        nx.octahedral_graph(),
        nx.dodecahedral_graph(),
        nx.icosahedral_graph(),
    ]
    rng = random.Random(seed)
    return rng.choice(solids).copy()


def generate_random_graph(
    size: int,
    p: float,
    *,
    seed: Optional[int] = None,
) -> Graph:
    """Return an ``Erdős–Rényi`` random graph with edge probability ``p``."""

    actual_seed = seed if seed is not None else _next_seed()
    graph = nx.erdos_renyi_graph(size, p, seed=actual_seed)
    if not nx.is_connected(graph):
        graph = repair_graph(graph)
    return graph


__all__ = [
    "Conjecture",
    "ConjectureResult",
    "check_subclasses",
    "compute_x_val_conjecture",
    "compute_y_val_conjecture",
    "compute_x_value",
    "compute_y_value",
    "evaluation",
    "evaluate_polynomial",
    "evaluate_conjecture",
    "test_conjecture_on_graph",
    "generate_bipartite_connected_graph",
    "generate_init_graph",
    "generate_init_graph_v2",
    "generate_random_graph",
    "generate_random_platonic_graph",
    "get_invariants",
    "load_conjectures",
    "mutation_add_edge",
    "mutation_add_vertex",
    "mutation_bipartition_neighborhood",
    "mutation_contraction",
    "mutation_remove_edge",
    "mutation_remove_vertex",
    "mutation_replace_vertex_by_clique",
    "mutation_replace_vertex_by_path",
    "mutation_replace_vertex_by_polyhedral",
    "mutation_replace_vertex_by_star",
    "mutation_subdivision",
    "repair_graph",
]
