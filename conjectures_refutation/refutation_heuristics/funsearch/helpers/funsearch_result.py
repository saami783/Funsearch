import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
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
    seed: Optional[int]|None
    funsearch_llm_provider: str|None
    funsearch_llm_temperature: str|None
    subclass: str|None
    cpus: int
    score_function_path: str
    score_function_name: str
    approx: bool
    np_hard_invariants: bool
    use_local_llm: str
    evaluate_time_limit: int
    reset_period_island: int
    time_limit: int

    x_value: Optional[float]|None
    y_value: Optional[float]|None


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


def build_result(
        cpus, score_function_path, score_function_name, approx, np_hard_invariants, use_local_llm, evaluate_time_limit, reset_period_island, time_limit,
        execution_time: Optional[float] = None,
        x_val: Optional[float] = None,
        y_val: Optional[float] = None,
        seed: Optional[int] = None,
        llm_provider: Optional[str] = None,
        llm_temperature: Optional[str] = None,
        subclass: Optional[str] = None,

) -> FunSearchResult:
    total_api = 0
    if os.path.exists("api_requests_count.txt"):
        with open("api_requests_count.txt", "r", encoding="utf-8") as f:
            total_api = sum(1 for _ in f)

    best_score = float('-inf')
    best_data = None

    if os.path.exists("funsearch_metrics.jsonl"):
        with open("funsearch_metrics.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line.strip())
                if data["score"] is not None and data["score"] > best_score:
                    best_score = data["score"]
                    best_data = data

    if best_data is None:
        return FunSearchResult(
            has_counterexample=False,
            counterexample_g6=None,
            size_of_counter_example=None,
            min_size=None,
            max_size=None,
            total_mutations_of_counterexample=None,
            score=None,
            total_graphs_generated=None,
            time=execution_time,
            total_api_requests=total_api,
            x_value=x_val,
            y_value=y_val,
            seed=seed,
            funsearch_llm_provider=llm_provider,
            funsearch_llm_temperature=llm_temperature,
            subclass=subclass,
            cpus=cpus,
            score_function_path=score_function_path,
            score_function_name=score_function_name,
            approx=approx,
            np_hard_invariants=np_hard_invariants,
            use_local_llm=use_local_llm,
            evaluate_time_limit=evaluate_time_limit,
            reset_period_island=reset_period_island,
            time_limit=time_limit
        )

    return FunSearchResult(
        has_counterexample=best_data["has_counterexample"],
        counterexample_g6=best_data["counterexample_g6"],
        size_of_counter_example=best_data["size_of_counter_example"],
        min_size=best_data["min_size"],
        max_size=best_data["max_size"],
        total_mutations_of_counterexample=best_data["total_mutations"] if best_data["has_counterexample"] else None,
        score=best_data["score"],
        total_graphs_generated=best_data["total_graphs_generated"],
        time=execution_time,
        total_api_requests=total_api,
        x_value=x_val,
        y_value=y_val,
        seed=seed,
        funsearch_llm_provider=llm_provider,
        funsearch_llm_temperature=llm_temperature,
        subclass=subclass,
        cpus=cpus,
        score_function_path=score_function_path,
        score_function_name=score_function_name,
        approx=approx,
        np_hard_invariants=np_hard_invariants,
        use_local_llm=use_local_llm,
        evaluate_time_limit=evaluate_time_limit,
        reset_period_island=reset_period_island,
        time_limit=time_limit
    )


def create_log_file(result: FunSearchResult):
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")

    output_dir = Path("out") / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    log_file_path = output_dir / "result.txt"

    result_dict = asdict(result)

    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write("=== RÉSULTATS FUNSEARCH ===\n")
        f.write("===========================\n\n")

        for key, value in result_dict.items():
            formatted_key = key.replace("_", " ").capitalize()

            formatted_value = value if value is not None else "N/A"

            f.write(f"{formatted_key}: {formatted_value}\n")

    print(f"[SAUVEGARDE] Résultats enregistrés dans le fichier : {log_file_path}")