# Automated Refutation of Conjectures in Graph Theory

An advanced computational framework designed to automatically find counterexamples to graph theory conjectures using local search and an independent implementation of Google DeepMind's **FunSearch** architecture.

---

## Verified Results

Between December 2025 and July 2026, this framework independently discovered valid counterexamples to 8 open conjectures in graph theory. Detailed mathematical proofs and reports are available in the [`conjectures_results/`](./conjectures_results/) directory.
We used the local search algorithm to find counterexamples.

| Target Conjecture | Conjecture | Counterexample size \(n\) | PDF Report |
| :--- | :--- | :---: | :--- |
| **Akbari et al. (Conj. 4.12)** | For every connected graph $G$ with line graph $L(G)$, $n^{+}(L(G)) \le n^{-}(L(G)) + 1$, that is $s(L(G)) \le 1$ | \(n = 33\) | [`view pdf`](./conjectures_results/Akbari_conjecture_4.12.pdf) |
| **TxGraffiti (Conjecture 9)** | If $G$ is a connected, cubic, and diamond-free graph, then $Z(G) \le \gamma(G) + 2$ | \(n = 14\) and \(n = 18\) | [`view pdf`](./conjectures_results/TxGraffiti_conjecture_9.pdf) |
| **Graffiti (Conjecture 63)** | If $G$ is a simple connected graph, then $f(G) \ge \lceil (\min(dist_{even}(v)) + b(G) + 1) / 3 \rceil$ | \(n = 16\) and \(n = 18\) | [`view pdf`](./conjectures_results/wowII/wowII_counterexamples_conjecture_63_&_85.pdf) |
| **Graffiti (Conjecture 64)** | If $G$ is a simple connected graph, then $f(G) \ge \left\lceil \sqrt{a(G) \cdot (1 + (n \bmod D(G)))} \right\rceil$ | \(n = 20\) | [`view pdf`](./conjectures_results/wowII/wowII_counterexample_conjecture_64.pdf) |
| **Graffiti (Conjecture 85)** | If $G$ is a simple connected graph, then $\text{tree}(G) \ge \lceil \sqrt{1 + 2 \min(dist_{even}(v))} \rceil$ | \(n = 16\) and \(n = 18\) | [`view pdf`](./conjectures_results/wowII/wowII_counterexamples_conjecture_63_&_85.pdf) |
| **Graffiti (Conjecture 91)** | If $G$ is a simple connected graph, then $b(G) \le 1 + f(G) \cdot \frac{\lceil l_{avg}(v) \rceil}{2}$ | \(n = 28\) | [`view pdf`](./conjectures_results/wowII/wowII_counterexample_conjecture_91.pdf) |
| **Graffiti (Conjecture 138)** | If $G$ is a simple connected graph, then $\text{path}(G) \ge (2 + u(G)) \cdot \text{dist}_{\min}(M(G^2))$ | \(n = 25\) | [`view pdf`](./conjectures_results/wowII/wowII_counterexample_conjecture_138.pdf) |
| **Graffiti (Conjecture 155)** | If $G$ is a simple connected graph, then $L_s(G) \ge 1 + \text{number of distinct orders of radial circles}$ | \(n = 24\) | [`view pdf`](./conjectures_results/wowII/wowII_counterexample_conjecture_155.pdf) |

---

## Installation

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