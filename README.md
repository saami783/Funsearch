## Réfutation automatique de conjectures en théorie des graphes

### Opérateurs disponibles

| Opérateur de mutation | Description                                                                                                                                                                                          |
| :--- |:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`add_edge`** | Ajoute une arête entre deux sommets non adjacents ou créez une nouvelle feuille.                                                                                                                     |
| **`remove_edge`** | Supprime une arête sans rompre la connexité.                                                                                                                                                         |
| **`add_vertex`** | Attache un nouveau sommet à exactement un sommet existant choisi au hasard (s’il y en a un).                                                                                                         |
| **`remove_vertex`** | Supprime un sommet non articulé si possible.                                                                                                                                                         |
| **`subdivision`** | Subdivise une arête aléatoire en y insérant un nouveau sommet.                                                                                                                                       |
| **`contraction`** | Contracte une arête aléatoire tout en conservant la simplicité du graphe.                                                                                                                            |
| **`replace_vertex_by_path`** | Remplace un sommet par un chemin et reconnectez les voisins au sommet central.                                                                                                                       |
| **`replace_vertex_by_star`** | Remplace un sommet par une étoile dont le centre reprend son rôle.                                                                                                                                   |
| **`replace_vertex_by_clique`**| Remplace un sommet par une clique et reconnectez les voisins aléatoirement.                                                                                                                          |
| **`replace_vertex_by_polyhedral`**| Remplace un sommet par un sous-graphe représentant un petit solide platonicien.                                                                                                                      |
| **`bipartition_neighborhood`**| Recâble le voisinage d’un sommet selon une bipartition aléatoire.                                                                                                                                    |

```bibtex
@Article{FunSearch2023,
  author  = {Romera-Paredes, Bernardino and Barekatain, Mohammadamin and Novikov, Alexander and Balog, Matej and Kumar, M. Pawan and Dupont, Emilien and Ruiz, Francisco J. R. and Ellenberg, Jordan and Wang, Pengming and Fawzi, Omar and Kohli, Pushmeet and Fawzi, Alhussein},
  journal = {Nature},
  title   = {Mathematical discoveries from program search with large language models},
  year    = {2023},
  doi     = {10.1038/s41586-023-06924-6}
}
```
