from __future__ import annotations
import argparse
import os
from multiprocessing import cpu_count
from pathlib import Path
from typing import Tuple

import ssl

_DEFAULT_MUTATION_NAMES_FALLBACK: Tuple[str, ...] = (
    "add_edge",
    "remove_edge",
    "add_vertex",
    "remove_vertex",
    "subdivision",
    "contraction",
    "replace_vertex_by_path",
    "replace_vertex_by_star",
    "replace_vertex_by_clique",
    "replace_vertex_by_polyhedral",
    "bipartition_neighborhood",
)


def _resolve_default_mutation_names() -> Tuple[str, ...]:
    try:
        from conjectures_refutation.refutation_heuristics.local_search import MUTATION_REGISTRY
        return tuple(MUTATION_REGISTRY.keys())
    except Exception:
        return _DEFAULT_MUTATION_NAMES_FALLBACK


DEFAULT_MUTATION_NAMES: Tuple[str, ...] = _resolve_default_mutation_names()

ssl._create_default_https_context = ssl._create_unverified_context


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extraction d'articles scientifiques et réfutation automatique d'objets "
            "en théorie des graphes."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    refutation_with_score_function = parser.add_argument_group("Réfutation avec un fonction de score déjà définie")
    refutation_with_score_function.add_argument(
        "--script",
        help=(
            "Chemin vers un script Python contenant une fonction de score de la forme "
            "score(G, min_size, max_size)."
        )
    )

    refutation_with_score_function.add_argument(
        "--function",
        help=(
            "Nom de la fonction de score à charger dans le script fourni via "
            "--with-score-function."
        )
    )

    refutation_with_score_function.add_argument(
        "--time-limit-llm-execution",
        help=(
            "Temps maximum accordé au code généré par le LLM pour s'exécuter sur un graphe (30 secondes par défaut)."
        )
    )

    refutation_with_score_function.add_argument(
        "--approx",
        action="store_true",
        default=False,
        help=(
            "Évaluation en deux étages : la fonction 'approx(G, min_size, max_size)' "
            "est utilisée en première pour l'évaluation, si le score est négatif alors "
            "la vraie fonction de score sera utilisée sur le graphe."
        )
    )

    refutation_with_score_function.add_argument(
        "--local-llm",
        action="store_true",
        default=False,
        help=(
            "Utilisation d'un LLM en local ou via requête API (OpenAI etc...). Ce paramètre permet de faire varier"
            "le nombre de requêtes simultanées envoyées. 2 requêtes pour un LLM en local vs 4 pour un LLM hébergé."
        )
    )

    parser.add_argument(
        "--strategy",
        choices=["hill_climbing", "funsearch"],
        default="hill_climbing",
        help=(
            "Stratégie de recherche de contre-exemples : hill climbing ou FunSearch."
        )
    )

    funsearch_group = parser.add_argument_group("Configuration FunSearch")
    funsearch_group.add_argument(
        "--llm",
        choices=["ollama", "gemini", "mistral", "codex", "deepseek", "gpt"],
        default=None,
        help=(
            "Backend LLM utilisé par FunSearch : [à définir]"
        )
    )

    funsearch_group = parser.add_argument_group("Configuration FunSearch")
    funsearch_group.add_argument(
        "--np-hard",
        action="store_true",
        default=False,
        help=(
            "Calcul d'une liste d'invariants NP-difficiles pour guider le LLM."
        )
    )

    funsearch_group.add_argument(
        "--funsearch-llm-temperature",
        type=float,
        default=None,
        help="Température d'échantillonnage du LLM utilisé par FunSearch."
    )

    funsearch_group.add_argument(
        "--funsearch-llm-max-tokens",
        type=int,
        default=None,
        help="Nombre maximal de tokens générés à chaque appel LLM de FunSearch."
    )

    parser.add_argument("--min-size", type=int, default=6, help="Nombre minimal de sommets des graphes testés.")
    parser.add_argument("--max-size", type=int, default=30, help="Nombre maximal de sommets des graphes testés.")
    parser.add_argument(
        "--subclass",
        default="",
        help=(
            "Sous-classe de graphes ciblée par la conjecture, "
            "ex. 'planar', 'connected,claw_free', 'bipartite'. "
            "Sépare plusieurs prédicats par des virgules. "
            "Si vide, aucune restriction de sous-classe n'est appliquée."
        ),
    )
    parser.add_argument("--time-limit", type=float, default=60.0 * 5, help="Temps maximal alloué à la recherche pour un objet donné, en secondes.")
    parser.add_argument("--neighbors", type=int, default=20, help="Nombre de voisins explorés par itération pour la recherche locale.")
    parser.add_argument("--max-mutations", type=int, default=2, help="Nombre maximal de mutations appliquées pour construire un voisin.")
    parser.add_argument("--stagnation", type=int, default=10, help="Nombre d'itérations sans amélioration avant une réinitialisation.")
    parser.add_argument("--margin", type=float, default=1e-3, help="Marge numérique requise pour accepter un contre-exemple.")
    parser.add_argument("--cache-limit", type=int, default=None, help="Nombre maximal d'évaluations conservées en cache.")
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire utilisée pour la reproductibilité.")
    parser.add_argument("--cpus", type=int, default=max(1, cpu_count() - 0), help="Nombre de processus workers ; <= 1 désactive le multiprocessing.")

    parser.add_argument(
        "--mutations",
        nargs="+",
        default=
            ["add_edge",
            "remove_edge",
            "add_vertex",
            "remove_vertex",
            "subdivision",
            "contraction",
            "replace_vertex_by_path",
            "replace_vertex_by_star",
            "replace_vertex_by_clique",
            "replace_vertex_by_polyhedral",
            "bipartition_neighborhood"],
        help="Opérateurs de mutation autorisés pendant la recherche."
    )

    args = parser.parse_args()

    return args


def create_or_wipe_identifiers(identifiers_path: Path) -> None:
    if identifiers_path.exists():
        print(f"Identifier file found: {identifiers_path}")
        print("Wipe file content...")
        identifiers_path.write_text("")

    if not identifiers_path.exists():
        print(f"Identifier file not found: {identifiers_path}")
        print("Creating file...")
        identifiers_path.touch()


def main():
    from conjectures_refutation.main import main as conjectures_refutation_main
    args = parse_args()

    print("Starting...")

    if not args.script:
        raise Exception("Veuillez spécifier le nom du script contenant la fonction de score (ex: --script conjecture_1.py).")
    print("Identification du fichier identifiers.txt ...")
    if not args.function:
        raise Exception("Veuillez spécifier (uniquement) le nom de la fonction de score à exécuter (ex: --function conj_1).")
    if args.strategy == "funsearch":
        if not args.llm:
            raise Exception("Veuillez spécifier le LLM à utiliser pour Funsearch (ex: --llm gpt-5.4).")

    if args.strategy == "hill_climbing":
        if args.np_hard:
            print("[Warning] le calcul d'invariants NP-Difficiles ne peut s'activer qu'avec Funsearch.")
        if args.llm_local:
            print("[Warning] l'utilisation d'un llm en local ou hébergé ne peut s'activer qu'avec Funsearch.")

    print(f"Affichage du nom du fichier : {args.script}")
    print(f"Affichage du nom de la fonction de score : {args.function}")

    actual_path = os.path.abspath(args.script)
    if not os.path.exists(actual_path):
            raise FileNotFoundError(f"Le fichier {args.script}.py est introuvable à la racine de l'application.")

    identifiers_file = "conjectures_refutation/data/identifiers.txt"
    identifiers_path = Path(identifiers_file)
    create_or_wipe_identifiers(identifiers_path)
    update_identifiers_by_arg(args.function, identifiers_path)

    run_params = {
        "min_size": args.min_size,
        "max_size": args.max_size,
        "time_limit": args.time_limit,
        "neighbors": args.neighbors,
        "max_mutations": args.max_mutations,
        "stagnation": args.stagnation,
        "margin": args.margin,
        "seed": args.seed,
        "mutation_names": args.mutations,
        "cpus": args.cpus,
        "llm": args.llm,
        "funsearch_llm_temperature": args.funsearch_llm_temperature,
        "funsearch_llm_max_tokens": args.funsearch_llm_max_tokens,
        "subclass": args.subclass,
        "score_function_path": args.script,
        "score_function_name": args.function,
        "approx": args.approx,
        "research_strategy": args.strategy,
        "funsearch_llm_provider": args.llm,
        "np_hard_invariants": args.np_hard,
        "use_local_llm": args.local_llm,
        "evaluate_time_limit": args.time_limit_llm_execution
    }

    print(f"Exécution du programme de réfutation avec le script python {args.script} pour la fonction de score {args.function}.")
    print(f"Utilisation de la stratégie de recherche {args.strategy}.")

    conjectures_refutation_main(**run_params)


def update_identifiers_by_arg(function: str, identifiers_path: Path):
    with identifiers_path.open("a", encoding="utf-8") as f:
        f.write(f"{function}\n")

if __name__ == "__main__":
    main()
