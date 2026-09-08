# Réfutation de conjectures en théorie des graphes

### Installation

Le programme nécessite Python en version >= 3.13.2

```shell
pip install -r requirements.txt
```

---

Exemple d'utilisation :

```shell
python main.py --script in/conjecture_1_54.py --function conjecture_1_54 --strategy funsearch --local-llm --time-limit 3600 --llm codex --time-limit-llm-execution 60
```

### Paramètres du programme

La liste des paramètres est [disponible ici](./doc/md/command.md).

---

### Sortie du programme

Après exécution, un fichier texte est généré dans `out/date_time/` contenant les résultats suivants :

- Has counterexample:
- Counterexample g6:
- Size of counter example:
- Min size:
- Max size:
- Total mutations of counterexample:
- Score:
- Total graphs generated:
- Time:
- Total api requests:
- Seed: 
- Funsearch llm provider:
- Funsearch llm temperature:
- Subclass: 
- Cpus:
- Score function path:
- Score function name:
- Approx:
- Np hard invariants:
- Use local llm:
- Evaluate time limit:
- Reset period island:
- Time limit:
- X value:
- Y value:

---

```bibtex
@Article{FunSearch2023,
  author  = {Romera-Paredes, Bernardino and Barekatain, Mohammadamin and Novikov, Alexander and Balog, Matej and Kumar, M. Pawan and Dupont, Emilien and Ruiz, Francisco J. R. and Ellenberg, Jordan and Wang, Pengming and Fawzi, Omar and Kohli, Pushmeet and Fawzi, Alhussein},
  journal = {Nature},
  title   = {Mathematical discoveries from program search with large language models},
  year    = {2023},
  doi     = {10.1038/s41586-023-06924-6}
}
```
