from __future__ import annotations

import random as _py_random
from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    base_accuracy: float = 0.40
    learning_gain: float = 0.10
    rt_mean_s: float = 0.08
    rt_sd_s: float = 0.02

    def __post_init__(self) -> None:
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _random(self) -> float:
        return float(self._rng.random()) if self._rng is not None else float(_py_random.random())

    def _choice(self, values: list[str]) -> str:
        if self._rng is not None and hasattr(self._rng, "choice"):
            return str(self._rng.choice(values))
        return str(_py_random.choice(values))

    def _normal(self) -> float:
        if self._rng is not None and hasattr(self._rng, "normal"):
            return float(self._rng.normal(self.rt_mean_s, self.rt_sd_s))
        if self._rng is not None and hasattr(self._rng, "gauss"):
            return float(self._rng.gauss(self.rt_mean_s, self.rt_sd_s))
        return float(_py_random.gauss(self.rt_mean_s, self.rt_sd_s))

    def act(self, obs: Observation) -> Action:
        valid_keys = list(obs.valid_keys or [])
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "rlwm_sampler", "reason": "no_valid_keys"})
        if obs.phase != "stimulus_response":
            return Action(key=valid_keys[0], rt_s=max(0.02, self._normal()), meta={"source": "rlwm_sampler"})

        factors = dict(obs.task_factors or {})
        correct_key = str(factors.get("correct_key") or "")
        iteration = int(factors.get("stimulus_iteration") or 1)
        set_size = max(2, int(factors.get("set_size") or 2))
        accuracy = min(0.97, max(1.0 / 3.0, self.base_accuracy + self.learning_gain * (iteration - 1) - 0.025 * (set_size - 2)))
        if correct_key in valid_keys and self._random() < accuracy:
            key = correct_key
            outcome = "learned_correct"
        else:
            alternatives = [key for key in valid_keys if key != correct_key] or valid_keys
            key = self._choice(alternatives)
            outcome = "sampled_error"
        return Action(
            key=key,
            rt_s=max(0.02, self._normal()),
            meta={"source": "rlwm_sampler", "outcome": outcome, "target_accuracy": accuracy},
        )
