import importlib.util
import os
import sys
from pathlib import Path
from typing import List

from conjectures_refutation.helpers.utility import load_conjectures

from conjectures_refutation.refutation_heuristics.local_search import (
    SearchConfig,
    SearchParameters,
    _derive_seed,
    process_all_conjectures,
)
from conjectures_refutation.refutation_heuristics.fun_search import evaluate


def load_hill_climbling(min_size, max_size, neighbors, max_mutations, time_limit, stagnation, margin, mutation_names, seed, identifiers, selected, output_dir, cpus):

    print("Initialisation des paramètres de recherche...")
    params = SearchParameters(
        min_size=min_size,
        max_size=max_size,
        neighbor_count=neighbors,
        max_mutations=max_mutations,
        time_limit=time_limit,
        stagnation_limit=stagnation,
        margin=margin,
        mutation_names=mutation_names,
        seed=seed,
        verbose=True,
    )

    print("Initialisation de la configuration de recherche...")

    config = SearchConfig(
        neighbour_count=params.neighbor_count,
        min_size=params.min_size,
        max_size=params.max_size,
        max_mutations=params.max_mutations,
        time_limit=params.time_limit,
        stagnation_limit=params.stagnation_limit,
        margin=params.margin,
        cache_size_limit=getattr(params, "cache_size_limit", None),
        mutation_names=params.mutation_names or None,
        verbose=params.verbose,
        seed=params.seed
    )
    if config.seed is not None:
        context_seed_pairs = [
            (identifier, _derive_seed(identifier, config.seed)) for identifier in identifiers
        ]
    else:
        context_seed_pairs = [(identifier, None) for identifier in identifiers]

    process_all_conjectures(
        selected,
        output_dir,
        config,
        show_plot=False,
        cpus=cpus,
        context_seed_pairs=context_seed_pairs
    )


def load_funsearch(min_size, max_size, score_fn):
    print("[DEBUG] : Nous sommes dans la fonction load_funsearch()")

    for i in range(min_size, max_size):
        score = evaluate(min_size, max_size, score_fn)
        print(f"Score du graphe pour la conjecture : {score}")


def main(min_size: int, max_size: int, time_limit: float, neighbors: int, max_mutations: int, stagnation: int, margin: float,
        seed: int, mutation_names: tuple[str, ...], cpus: int,
        score_function_path: str, score_function_name: str,
         research_strategy: str,
         approx: bool,
         funsearch_llm_provider: str | None,
         funsearch_llm_temperature: float | None,
         funsearch_llm_max_tokens: int | None,
         subclass: str | None,
         **_ignored_kwargs) -> None:

    output_dir = Path("out")
    identifiers = _load_identifiers(Path("conjectures_refutation/data/identifiers.txt"))

    dataset = load_conjectures("conjectures_refutation/data/benchmark.csv")
    if not dataset:
        raise SystemExit("No conjectures were loaded from benchmark.csv")

    by_identifier = {row.get("ID"): row for row in dataset if row.get("ID") is not None}
    selected: List[dict] = []
    missing: List[str] = []

    for identifier in identifiers:
        match = by_identifier.get(identifier)
        if match is not None:
            entry = dict(match)
            entry.setdefault("subclass", "")
            selected.append(entry)
            continue

        actual_path = os.path.abspath(score_function_path)

        module_dir = os.path.dirname(actual_path)
        module_name = os.path.basename(actual_path)
        if module_name.endswith('.py'):
            module_name = module_name[:-3]

        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        try:
            custom_module = importlib.import_module(module_name)
        except Exception as e:
            raise ImportError(f"Impossible d'importer le fichier {module_name}.py : {e}")

        score_fn = getattr(custom_module, score_function_name)
        if score_fn is None or not callable(score_fn):
            raise AttributeError(f"La fonction '{score_function_name}' n'existe pas ou n'est pas appelable dans '{actual_path}'.")

        approx_fn = None
        if approx:
            approx_fn = getattr(custom_module, "approx", None)
            if approx_fn is None or not callable(approx_fn):
                raise AttributeError(f"--approx demandé mais aucune fonction 'approx(G, min_size, max_size) n'existe dans '{actual_path}'.")

            print(f"Recherche approchée activée. Si un graphe candidat obtient un score négatif alors '{score_function_name}' sera appelée sur le candidat.")

        selected.append(
            {
                "ID": identifier,
                "conjecture": f"Custom scoring function {identifier}",
                "subclass": "",
                "score_function": score_fn,
                "approx_function": approx_fn,
            }
        )
        continue

    if research_strategy == "hill_climbing":
        load_hill_climbling(min_size, max_size, neighbors, max_mutations, time_limit, stagnation, margin, mutation_names, seed, identifiers, selected, output_dir, cpus)
    else:
        score_fn = selected[0]["score_function"]
        load_funsearch(min_size, max_size, score_fn)


def _load_identifiers(path: Path) -> List[str]:
    if not path.exists():
        raise SystemExit(f"Identifier file not found: {path}")
    identifiers: List[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            value = line.strip()
            if value:
                identifiers.append(value)
    if not identifiers:
        raise SystemExit(f"Identifier file {path} is empty")
    return identifiers
