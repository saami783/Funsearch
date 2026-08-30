import json
from dataclasses import dataclass
from typing import Optional
import networkx as nx


@dataclass(slots=True)
class FunSearchResult:
    """Outcome of a Funsearch run against a single conjecture."""

    has_counterexample: bool
    counterexample_g6: str|None
    size_of_counter_example: int|None
    min_size: int|None
    max_size: int|None
    total_mutations_of_counterexample: int|None
    score: float|None
    total_graphs_generated: int | None

    time: float|None
    total_api_requests: int|None

    x_value: Optional[float]|None
    y_value: Optional[float]|None
    seed: Optional[int]|None
    funsearch_llm_provider: str|None
    funsearch_llm_temperature: str|None
    subclass: str|None


def log_result(G, score, total_mutations, total_graphs_generated, min_size, max_size):
    is_counterexample = (score is not None) and (score > 0)

    log_data = {
        "has_counterexample": is_counterexample,
        "counterexample_g6": nx.to_graph6_bytes(G, header=False).decode('utf-8').strip() if is_counterexample else None,
        "size_of_counter_example": G.number_of_nodes() if is_counterexample else None,
        "total_graphs_generated": total_graphs_generated,
        "total_mutations": total_mutations,
        "score": score,
        "min_size": min_size,
        "max_size": max_size
    }

    with open("funsearch_metrics.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data) + "\n")