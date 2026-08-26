import importlib.util
import os
import sys
from pathlib import Path
from typing import List

from conjectures_refutation.helpers import scores_function
from conjectures_refutation.helpers.utility import load_conjectures

from conjectures_refutation.refutation_heuristics.local_search import (
    SearchConfig,
    SearchParameters,
    _derive_seed,
    process_all_conjectures,
)


def main(min_size: int, max_size: int, time_limit: float, neighbors: int, max_mutations: int, stagnation: int, margin: float,
        seed: int, mutation_names: tuple[str, ...], cpus: int,
        score_function_path: str, score_function_name: str,
         research_strategy: str = "hill_climbing",
         approx: bool = False,
         funsearch_llm_provider: str | None = None,
         funsearch_llm_temperature: float | None = None,
         funsearch_llm_max_tokens: int | None = None,

         subclass: str = "",
         **_ignored_kwargs) -> None:

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

        if score_function_path is not None:
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

            print("conjectures_refutation/main.py")

            score_fn = getattr(custom_module, score_function_name)
            if score_fn is None or not callable(score_fn):
                raise AttributeError(
                    f"La fonction '{score_function_name}' n'existe pas ou n'est pas appelable dans '{actual_path}'.")

            approx_fn = None
            if approx:
                approx_fn = getattr(custom_module, "approx", None)
                if approx_fn is None or not callable(approx_fn):
                    raise AttributeError(
                        f"--approx demandé mais aucune fonction 'approx(G, min_size, max_size)' "
                        f"n'existe dans '{actual_path}'.")
                print(f"Mode approx activé : 'approx' guide la recherche, "
                      f"'{score_function_name}' confirme les contre-exemples.")

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

        print("Aucun type détecté, récupération de la fonction de score de "
              "chaque identifiant dans le fichier identifiers...")
        score_fn = getattr(scores_function, f"conj_{identifier}", None)

        if score_fn is None:
            # missing.append(identifier)
            print(f"[{identifier}] - Fonction de score ignorée. L'énoncé est ambigu ou incomplet. Réfutation annulée.")
            continue

        selected.append(
            {
                "ID": identifier,
                "conjecture": f"Custom scoring function {identifier}",
                "subclass": "",
                # "score_function": score_fn,
            }
        )

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
        seed=params.seed,
        # funsearch_llm_provider=funsearch_llm_provider,
        # funsearch_llm_temperature=funsearch_llm_temperature,
        # funsearch_llm_max_tokens=funsearch_llm_max_tokens,
        # subclass=subclass or "",
        # score_function_file=score_function_path,
        # score_function_name=("approx" if approx else score_function_name),
    )
    if config.seed is not None:
        context_seed_pairs = [
            (identifier, _derive_seed(identifier, config.seed)) for identifier in identifiers
        ]
    else:
        context_seed_pairs = [(identifier, None) for identifier in identifiers]

    output_dir = Path("out")

    process_all_conjectures(
        selected,
        output_dir,
        config,
        show_plot=False,
        cpus=cpus,
        context_seed_pairs=context_seed_pairs,
        # research_strategy=research_strategy
    )


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
