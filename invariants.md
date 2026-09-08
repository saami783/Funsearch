## Invariants calculés par défaut

Les invariants sont à définir dans [funsearch_invariants.py](./conjectures_refutation/refutation_heuristics/funsearch/helpers/funsearch_invariants.py). 

| Invariant                           | Description                                            |
|:------------------------------------|:-------------------------------------------------------|
| **`is_connected`**                  | Retourne vrai si $G$ est un graphe connexe             |
| **`is_complete`**                   | Retourne vrai si $G$ est un graphe complet             |
| **`is_tree`**                       | Retourne vrai si $G$ est un arbre                      |
| **`is_path`**                       | Retourne vrai si $G$ est un chemin                     |
| **`is_star`**                       | Retourne vrai si $G$ est une étoile                    |
| **`is_planar`**                     | Retourne vrai si $G$ est un graphe planaire            |
| **`is_chordal`**                    | Retourne vrai si $G$ est un graphe cordal              |
| **`is_bipartite`**                  | Retourne vrai si $G$ est un graphe biparti             |
| **`is_triangle_free`**              | Retourne vrai si $G$ est un graphe sans triangle       |
| **`is_eulerian`**                   | Retourne vrai si $G$ est un graphe eulérien            |
| **`is_hamiltonian`**                | Retourne vrai si $G$ est un graphe hamiltonien         |
| **`is_regular`**                    | Retourne vrai si $G$ est un graphe régulier            |
| **`contains_induced_subgraph`**     | Retourne vrai si $G$ contient des sous-graphes induits |
| **`is_claw_free`**                  | Retourne vrai si $G$ est un graphe sans griffe         |
| **`is_bull_free`**                  | Retourne vrai si $G$ est un graphe à bulles            |
| **`is_paw_free`**                   | Retourne vrai si $G$ est un graphe sans pattes         |
| **`is_diamond_free`**               | Retourne vrai si $G$ est un graphe sans diamants       |
| **`diameter`**                      | Retourne le diamètre de $G$                            |
| **`radius`**                        | Retourne le rayon de $G$                               |
| **`number_of_components`**          | Retourne le nombre de composants de $G$                |
| **`largest_component_ratio`**       |                                                        |
| **`degree_variance`**               |                                                        |
| **`average_clustering`**            |                                                        |
| **`number_of_leaves`**              |                                                        |
| **`number_of_articulation_points`** |                                                        |
| **`number_of_bridges`**             |                                                        |
| **`girth`**                         |                                                        |
| **`circumference`**                 |                                                        |
| **`size`**                          | Retourne le nombre d'arêtes de $G$                     |
| **`order`**                         | Retourne le nombre de sommets de $G$                   |
| **`max_degree`**                    | Retourne le degré maximum de $G$                       |
| **`min_degree`**                    | Retourne le degré minimum de $G$                       |
| **`avg_degree`**                    | Retourne le degré moyen de $G$                         |
| **`density`**                       | Retourne la densité de $G$                             |
| **`matching_number`**               |                                                        |
| **`spanning_tree_number`**          |                                                        |
| **`vertex_connectivity`**           |                                                        |
| **`edge_connectivity`**             |                                                        |
| **`triangle_number`**               | Retourne le nombre de triangles de $G$                 |
| **`proximity`**                     |                                                        |
| **`remoteness`**                    |                                                        |
| **`harmonic_index`**                |                                                        |
| **`randic_index`**                  |                                                        |
| **`modified_zagreb_2`**             |                                                        |
| **`spectrum`**                      |                                                        |
| **`largest_eigenvalue`**            |                                                        |
| **`largest_distance_eigenvalue`**   |                                                        |
| **`connectivity`**                  |                                                        |
| **`p_A`**                           |                                                        |
| **`m`**                             |                                                        |


### Invariants NP-Difficiles

À utiliser avec l'argument `--np-hard` pour ajouter le calcul des invariants np-difficile

| Invariant                          | Description                                                                                                                                                                                        |
|:-----------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`treewidth`**                     |                                                                                                                                                                                                    |
| **`longest_path`**                  |                                                                                                                                                                                                    |
| **`longest_induced_path`**                   |                                                                                                                                                                                                    |
| **`longest_induced_cycle`**                |                                                                                                                                                                                                    |
| **`chromatic_number`**                  |                                                                                                                                                                                                    |
| **`chromatic_index`**                  |                                                                                                                                                                                                    |
| **`clique_number`**       |                                                                                                                                                                                                    |
| **`independence_number`**       |                                                                                                                                  |
| **`vertex_cover_number`**     |                                                                                                                         |
| **`feedback_vertex_set_number`** |                                                                                                                     |
| **`domination_number`**     |                                                                                                                                   |
| **`total_domination_number`**     |                                                                                                                                   |
| **`independent_domination_number`**     |                                                                                                                                   |
