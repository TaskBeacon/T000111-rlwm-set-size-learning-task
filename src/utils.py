from __future__ import annotations

import colorsys
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class TrialSpec:
    block_id: str
    block_idx: int
    set_size: int
    stimulus_id: str
    shape_id: str
    fill_color: str
    correct_key: str
    stimulus_iteration: int
    sequence_index: int
    delay_trials: int | None


@dataclass(frozen=True)
class BlockPlan:
    block_id: str
    block_idx: int
    set_size: int
    items: tuple[TrialSpec, ...]
    trials: tuple[TrialSpec, ...]


def stable_subject_seed(subject_id: Any, overall_seed: int) -> int:
    """Return the same unsigned FNV-1a seed used by the web port."""

    value = 2_166_136_261
    for byte in f"{overall_seed}:{subject_id}".encode("utf-8"):
        value ^= byte
        value = (value * 16_777_619) & 0xFFFFFFFF
    return value


class SeededRng:
    """Small cross-language LCG with deterministic choice and shuffle methods."""

    def __init__(self, seed: int) -> None:
        self.state = int(seed) & 0xFFFFFFFF

    def random(self) -> float:
        self.state = (1_664_525 * self.state + 1_013_904_223) & 0xFFFFFFFF
        return self.state / 4_294_967_296

    def choice(self, values: Sequence[str]) -> str:
        if not values:
            raise ValueError("cannot choose from an empty sequence")
        return values[int(self.random() * len(values))]

    def shuffle(self, values: list[int]) -> None:
        for index in range(len(values) - 1, 0, -1):
            swap_index = int(self.random() * (index + 1))
            values[index], values[swap_index] = values[swap_index], values[index]


def _hex_color(block_idx: int, item_idx: int) -> str:
    hue = ((block_idx * 37 + item_idx * 61) % 360) / 360.0
    saturation = 0.62 + 0.08 * ((block_idx + item_idx) % 3)
    value = 0.72 + 0.08 * ((2 * block_idx + item_idx) % 3)
    red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
    return (
        f"#{int(red * 255 + 0.5):02X}"
        f"{int(green * 255 + 0.5):02X}"
        f"{int(blue * 255 + 0.5):02X}"
    )


def _subject_block_order(schedule: Sequence[int], seed: int) -> list[int]:
    order = [int(value) for value in schedule]
    if not order:
        raise ValueError("set_size_schedule cannot be empty")
    rotation = seed % len(order)
    order = order[rotation:] + order[:rotation]
    if (seed // max(1, len(order))) % 2:
        order.reverse()
    return order


def _trial_order(set_size: int, iterations: int, rng: SeededRng) -> list[int]:
    order: list[int] = []
    previous_last: int | None = None
    for _ in range(iterations):
        round_items = list(range(set_size))
        rng.shuffle(round_items)
        if previous_last is not None and set_size > 1 and round_items[0] == previous_last:
            swap_idx = next(index for index, item in enumerate(round_items[1:], start=1) if item != previous_last)
            round_items[0], round_items[swap_idx] = round_items[swap_idx], round_items[0]
        order.extend(round_items)
        previous_last = round_items[-1]
    return order


def build_block_plans(
    *,
    subject_id: Any,
    overall_seed: int,
    set_size_schedule: Sequence[int],
    iterations_per_stimulus: int,
    shape_ids: Sequence[str],
    response_keys: Sequence[str],
) -> list[BlockPlan]:
    """Build block-level stimulus/action mappings and interleaved trial schedules."""

    shapes = [str(value) for value in shape_ids]
    keys = [str(value).strip().lower() for value in response_keys]
    if len(shapes) < 6:
        raise ValueError("shape_ids must contain at least six concrete shapes")
    if len(keys) != 3 or len(set(keys)) != 3:
        raise ValueError("response_keys must contain exactly three unique keys")
    if iterations_per_stimulus < 1:
        raise ValueError("iterations_per_stimulus must be positive")

    session_seed = stable_subject_seed(subject_id, int(overall_seed))
    ordered_sizes = _subject_block_order(set_size_schedule, session_seed)
    plans: list[BlockPlan] = []
    for block_idx, set_size in enumerate(ordered_sizes):
        if set_size not in {2, 3, 4, 5, 6}:
            raise ValueError(f"unsupported RLWM set size: {set_size}")
        rng = SeededRng(session_seed + (block_idx + 1) * 1009)
        block_id = f"rlwm_block_{block_idx + 1:02d}_ss{set_size}"
        item_templates: list[TrialSpec] = []
        for item_idx in range(set_size):
            shape_id = shapes[(block_idx + item_idx) % len(shapes)]
            item_templates.append(
                TrialSpec(
                    block_id=block_id,
                    block_idx=block_idx,
                    set_size=set_size,
                    stimulus_id=f"b{block_idx + 1:02d}_item{item_idx + 1:02d}",
                    shape_id=shape_id,
                    fill_color=_hex_color(block_idx, item_idx),
                    correct_key=rng.choice(keys),
                    stimulus_iteration=0,
                    sequence_index=-1,
                    delay_trials=None,
                )
            )

        order = _trial_order(set_size, int(iterations_per_stimulus), rng)
        counts = [0] * set_size
        last_seen: list[int | None] = [None] * set_size
        trials: list[TrialSpec] = []
        for sequence_index, item_idx in enumerate(order):
            counts[item_idx] += 1
            prior_index = last_seen[item_idx]
            template = item_templates[item_idx]
            trials.append(
                TrialSpec(
                    block_id=template.block_id,
                    block_idx=template.block_idx,
                    set_size=template.set_size,
                    stimulus_id=template.stimulus_id,
                    shape_id=template.shape_id,
                    fill_color=template.fill_color,
                    correct_key=template.correct_key,
                    stimulus_iteration=counts[item_idx],
                    sequence_index=sequence_index,
                    delay_trials=None if prior_index is None else sequence_index - prior_index,
                )
            )
            last_seen[item_idx] = sequence_index
        plans.append(
            BlockPlan(
                block_id=block_id,
                block_idx=block_idx,
                set_size=set_size,
                items=tuple(item_templates),
                trials=tuple(trials),
            )
        )
    return plans


def summarize_learning(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    records = [dict(row) for row in rows]
    by_size: dict[str, dict[str, Any]] = {}
    for set_size in range(2, 7):
        subset = [row for row in records if int(row.get("set_size", -1)) == set_size]
        scored = [row for row in subset if not bool(row.get("timed_out"))]
        by_size[str(set_size)] = {
            "trials": len(subset),
            "responses": len(scored),
            "accuracy": (
                sum(bool(row.get("response_correct")) for row in scored) / len(scored)
                if scored
                else None
            ),
        }
    return {
        "total_trials": len(records),
        "response_count": sum(not bool(row.get("timed_out")) for row in records),
        "correct_count": sum(bool(row.get("response_correct")) for row in records),
        "by_set_size": by_size,
    }
