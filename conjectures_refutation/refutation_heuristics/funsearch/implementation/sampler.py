# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Class for sampling new programs."""
import time
from collections.abc import Collection, Sequence
import requests
import numpy as np

from conjectures_refutation.refutation_heuristics.funsearch.implementation import evaluator
from conjectures_refutation.refutation_heuristics.funsearch.implementation import programs_database


def _trim_preface_of_body(sample: str) -> str:
    """
    Nettoie la réponse du LLM pour ne garder que le corps de la fonction.
    """
    if "```python" in sample:
        sample = sample.split("```python")[1]
    if "```" in sample:
        sample = sample.split("```")[0]

    lines = sample.splitlines()
    func_body_lineno = 0
    find_def_declaration = False

    for lineno, line in enumerate(lines):
        if line.strip().startswith('def '):
            func_body_lineno = lineno
            find_def_declaration = True
            break

    if find_def_declaration:
        code = ''
        for line in lines[func_body_lineno + 1:]:
            code += line + '\n'
        return code

    return sample


class LLM:
    """Language model that predicts continuation of provided source code."""

    def __init__(self, samples_per_prompt: int) -> None:
        self._samples_per_prompt = samples_per_prompt
        # L'adresse de ton wrapper sur le réseau local (à adapter)
        self._url = 'http://192.168.X.X:11434/api/generate'

    def _draw_sample(self, prompt: str) -> str:
        """Appelle l'API du LLM pour générer une complétion."""

        with open("api_requests_count.txt", "a", encoding="utf-8") as f:
            f.write("1\n")

        try:
            payload = {
                "prompt": prompt,
                "use_local_llm": False,
                "temperature": 0.8
            }

            response = requests.post(self._url, json=payload, timeout=60.0)

            if response.status_code == 200:
                raw_code = response.json().get("response", "")
                clean_code = _trim_preface_of_body(raw_code)
                return clean_code
            else:
                print(f"[LLM] Code HTTP inattendu : {response.status_code}")
                return "    return 0.0\n"

        except Exception as e:
            print(f"[LLM] Erreur de génération : {e}")
            return "    return 0.0\n"

    def draw_samples(self, prompt: str) -> Collection[str]:
        """Returns multiple predicted continuations of `prompt`."""
        return [self._draw_sample(prompt) for _ in range(self._samples_per_prompt)]


class Sampler:
    """Node that samples program continuations and sends them for analysis."""

    def __init__(
            self,
            database: programs_database.ProgramsDatabase,
            evaluators: Sequence[evaluator.Evaluator],
            samples_per_prompt: int,
            end_time: float
    ) -> None:
        self._database = database
        self._evaluators = evaluators
        self._llm = LLM(samples_per_prompt)
        self._end_time = end_time

    def sample(self):
        """Continuously gets prompts, samples programs, sends them for analysis."""
        while True:
            if self._end_time is not None and time.time() > self._end_time:
                print("[Sampler] Temps limite écoulé. Arrêt du programme...")
                break

            prompt = self._database.get_prompt()
            samples = self._llm.draw_samples(prompt.code)
            # This loop can be executed in parallel on remote evaluator machines.
            for sample in samples:
                chosen_evaluator = np.random.choice(self._evaluators)
                chosen_evaluator.analyse(
                    sample, prompt.island_id, prompt.version_generated)