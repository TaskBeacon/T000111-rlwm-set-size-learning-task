from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from psyflow import StimUnit, next_trial_id, set_trial_context


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run one deterministic stimulus-action learning trial."""

    if is_dataclass(condition):
        trial: Mapping[str, Any] = asdict(condition)
    elif isinstance(condition, Mapping):
        trial = dict(condition)
    else:
        raise TypeError(f"Expected RLWM trial mapping, got {type(condition).__name__}")

    trial_id = int(next_trial_id())
    block_id_value = str(block_id or trial["block_id"])
    block_idx_value = int(block_idx if block_idx is not None else trial["block_idx"])
    set_size = int(trial["set_size"])
    stimulus_id = str(trial["stimulus_id"])
    shape_id = str(trial["shape_id"])
    fill_color = str(trial["fill_color"])
    correct_key = str(trial["correct_key"]).lower()
    response_keys = [str(key).lower() for key in settings.response_keys]
    response_window = float(settings.response_window_s)

    factors = {
        "set_size": set_size,
        "stimulus_id": stimulus_id,
        "shape_id": shape_id,
        "fill_color": fill_color,
        "correct_key": correct_key,
        "stimulus_iteration": int(trial["stimulus_iteration"]),
        "sequence_index": int(trial["sequence_index"]),
        "delay_trials": trial.get("delay_trials"),
        "block_idx": block_idx_value,
    }
    trial_data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_id_value,
        "block_idx": block_idx_value,
        "condition": f"set_size_{set_size}",
        "condition_id": f"set_size_{set_size}",
        **factors,
    }

    stimulus = StimUnit("stimulus_response", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.rebuild(
            shape_id,
            fillColor=fill_color,
            lineColor="#111827",
            update_cache=False,
        )
    )
    set_trial_context(
        stimulus,
        trial_id=trial_id,
        phase="stimulus_response",
        deadline_s=response_window,
        valid_keys=response_keys,
        block_id=block_id_value,
        condition_id=f"set_size_{set_size}",
        task_factors={**factors, "stage": "stimulus_response"},
        stim_id=f"{shape_id}:{stimulus_id}",
        stim_features={"shape_id": shape_id, "fill_color": fill_color},
    )
    stimulus.capture_response(
        keys=response_keys,
        correct_keys=[correct_key],
        duration=response_window,
        onset_trigger=settings.triggers.get(f"stimulus_ss{set_size}_onset"),
        response_trigger={
            response_keys[0]: settings.triggers.get("response_key_1"),
            response_keys[1]: settings.triggers.get("response_key_2"),
            response_keys[2]: settings.triggers.get("response_key_3"),
        },
        timeout_trigger=settings.triggers.get("response_timeout"),
    ).to_dict(trial_data)

    response_key = str(stimulus.get_state("response", "") or "").lower()
    response_rt = stimulus.get_state("rt", None)
    timed_out = not bool(response_key)
    response_correct = bool(response_key == correct_key)
    if timed_out:
        feedback_id = "feedback_timeout"
        feedback_trigger = settings.triggers.get("feedback_timeout")
        outcome = "timeout"
    elif response_correct:
        feedback_id = "feedback_correct"
        feedback_trigger = settings.triggers.get("feedback_correct")
        outcome = "correct"
    else:
        feedback_id = "feedback_incorrect"
        feedback_trigger = settings.triggers.get("feedback_incorrect")
        outcome = "incorrect"

    trial_data.update(
        {
            "response_key": response_key,
            "response_rt": float(response_rt) if isinstance(response_rt, (int, float)) else None,
            "response_correct": response_correct,
            "timed_out": timed_out,
            "reward": 1 if response_correct else 0,
            "outcome": outcome,
        }
    )

    feedback = StimUnit("feedback", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get(feedback_id)
    )
    set_trial_context(
        feedback,
        trial_id=trial_id,
        phase="feedback",
        deadline_s=float(settings.feedback_duration_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=f"set_size_{set_size}",
        task_factors={**factors, "stage": "feedback", "outcome": outcome, "reward": trial_data["reward"]},
        stim_id=feedback_id,
    )
    feedback.show(
        duration=float(settings.feedback_duration_s),
        onset_trigger=feedback_trigger,
    ).to_dict(trial_data)

    iti = StimUnit("inter_trial_interval", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("fixation")
    )
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="inter_trial_interval",
        deadline_s=float(settings.iti_duration_s),
        valid_keys=[],
        block_id=block_id_value,
        condition_id=f"set_size_{set_size}",
        task_factors={**factors, "stage": "inter_trial_interval"},
        stim_id="fixation",
    )
    iti.show(
        duration=float(settings.iti_duration_s),
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)
    return trial_data
