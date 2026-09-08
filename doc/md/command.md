## Paramètres globaux :

| Argument | Description                                                                                  |
| :--- |:---------------------------------------------------------------------------------------------|
| **`--script`** | Chemin vers un script Python contenant une fonction de score de la forme score(G, min_size, max_size).              |
| **`--function`** | Nom de la fonction de score à charger dans le script spécifié via `--script`.                                                 |
| **`--approx`** | Évaluation en deux étages : la fonction 'approx(G, min_size, max_size)' est utilisée en première pour l'évaluation du graphe. Si le score est négatif alors la vraie fonction de score sera utilisée sur le graphe. |
| **`--strategy`** | Stratégie de recherche de contre-exemples : `hill_climbing` ou `funsearch`.                                                 |
| **`--min-size`** | Nombre minimal de sommets des graphes testés : 6 par défaut.                              |
| **`--max-size`** | Nombre maximal de sommets des graphes testés : 30 par défaut.                    |
| **`--time-limit`** | Temps maximal alloué à la recherche pour un objet donné, en secondes : 5 minutes par défaut.             |
| **`--seed`** | Graine aléatoire utilisée pour la reproductibilité : 42 par défaut.                         | |


## Paramètres liés à FunSearch :

Ces paramètres nécessitent d'avoir défini au préalable les paramètres suivants :
- --script
- --function
- --strategy

| Argument | Description                                                                                  |
| :--- |:---------------------------------------------------------------------------------------------|
| **`--local-llm`** | Utilisation d'un LLM en local ou via requête API (OpenAI etc...). Ce paramètre permet de faire varier le nombre de requêtes simultanées envoyées. 2 requêtes pour un LLM en local vs 4 pour un LLM hébergé.              |
| **`--llm`** | LLM utilisé par FunSearch : (à définir et à implémenter).                                                 |
| **`--time-limit-llm-execution`** | Temps maximum accordé au code généré par le LLM pour s'exécuter sur un graphe : 30 secondes par défaut. |
| **`--reset-period-island`** | Temps au bout duquel FunSearch supprime les mauvaises îles pour relancer l'exploration à partir des meilleures découvertes : 4 heures par défaut.                                                 |
| **`--np-hard`** | Calculs d'une liste d'invariants NP-difficiles pour guider le LLM. La liste des invariants NP-Difficiles est [disponible ici](invariants.md).|                              |
| **`--subclass`** | Sous-classe de graphes ciblée par la conjecture. Si vide, aucune restriction de sous-classe n'est appliquée, le programme partira d'un graphe vide et apprendra la structure du graphe à construire. Les familles de graphes sont à définir dans [subclass.py](../../conjectures_refutation/refutation_heuristics/funsearch/helpers/subclass.py).                 |

## Paramètres liés au Hill Climbing :

| Argument | Description                                                                                  |
| :--- |:---------------------------------------------------------------------------------------------|
| **`--neighbors`** | Nombre de voisins explorés par itération pour la recherche locale : 20 par défaut.              |
| **`--max-mutations`** | Nombre maximal de mutations appliquées pour construire un voisin : 2 par défaut.                                          |
| **`--stagnation`** | Nombre d'itérations sans amélioration avant une réinitialisation : 10 par défaut.|
| **`--margin`** | Marge numérique requise pour accepter un contre-exemple : 1e-3 par défaut.                                                 |
| **`--cache-limit`** | Nombre maximal d'évaluations conservées en cache : None par défaut.                              |
| **`--cpus`** | Nombre de processus workers ; <= 1 désactive le multiprocessing : le nombre de cpus de la machine - 1 par défaut.                    |
| **`--mutations`** | Opérateurs de mutation autorisés pendant la recherche. [Voir la liste par défaut](mutations.md). Les opérateurs sont à définir dans [funsearch_mutations.py](../../conjectures_refutation/refutation_heuristics/funsearch/helpers/funsearch_mutations.py).                       |
