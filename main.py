from __future__ import annotations

import json
from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    next_trial_id,
    parse_task_run_options,
    runtime_context,
    set_trial_context,
)

from src import BlockPlan, build_block_plans, run_trial, summarize_learning


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _familiarization_positions(set_size: int, spacing_px: float) -> list[tuple[float, float]]:
    start = -spacing_px * (set_size - 1) / 2.0
    return [(start + item_idx * spacing_px, -20.0) for item_idx in range(set_size)]


def _show_familiarization(
    *,
    plan: BlockPlan,
    total_blocks: int,
    win,
    kb,
    settings,
    stim_bank,
    trigger_runtime,
) -> None:
    unit = StimUnit("block_familiarization", win, kb, runtime=trigger_runtime)
    unit.add_stim(
        stim_bank.get_and_format(
            "familiarization_header",
            block_number=plan.block_idx + 1,
            total_blocks=total_blocks,
            set_size=plan.set_size,
        )
    )
    positions = _familiarization_positions(plan.set_size, float(settings.preview_spacing_px))
    for item, position in zip(plan.items, positions):
        unit.add_stim(
            stim_bank.rebuild(
                item.shape_id,
                pos=position,
                fillColor=item.fill_color,
                lineColor="#111827",
                update_cache=False,
            )
        )
    preview_trial_id = int(next_trial_id())
    set_trial_context(
        unit,
        trial_id=preview_trial_id,
        phase="block_familiarization",
        deadline_s=None,
        valid_keys=[str(settings.continue_key)],
        block_id=plan.block_id,
        condition_id=f"set_size_{plan.set_size}",
        task_factors={
            "stage": "block_familiarization",
            "block_idx": plan.block_idx,
            "set_size": plan.set_size,
            "stimulus_ids": [item.stimulus_id for item in plan.items],
        },
        stim_id="familiarization_header+block_stimulus_set",
    )
    unit.wait_and_continue(keys=[str(settings.continue_key)])


def run(options: TaskRunOptions) -> None:
    """Run the deterministic RLWM set-size learning task."""

    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))
    output_dir: Path | None = None
    runtime_scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        if options.mode == "qa":
            subject_data = {"subject_id": "qa111"}
        elif options.mode == "sim":
            participant_id = "sim111"
            if runtime_ctx is not None and runtime_ctx.session is not None:
                participant_id = str(runtime_ctx.session.participant_id or participant_id)
            subject_data = {"subject_id": participant_id}
        else:
            subject_data = SubInfo(cfg["subform_config"]).collect()

        settings = TaskSettings.from_dict(cfg["task_config"])
        settings.add_subinfo(subject_data)
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.save_path = str(output_dir)
            prefix = "qa" if options.mode == "qa" else "sim"
            settings.res_file = str(output_dir / f"{prefix}_trace.csv")
            settings.log_file = str(output_dir / f"{prefix}_psychopy.log")
            settings.json_file = str(output_dir / f"{prefix}_settings.json")

        settings.triggers = cfg["trigger_config"]
        trigger_runtime = (
            initialize_triggers(mock=True)
            if options.mode in ("qa", "sim")
            else initialize_triggers(cfg)
        )
        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, cfg["stim_config"]).preload_all()
        settings.save_to_json()

        plans = build_block_plans(
            subject_id=subject_data["subject_id"],
            overall_seed=int(settings.overall_seed),
            set_size_schedule=settings.set_size_schedule,
            iterations_per_stimulus=int(settings.iterations_per_stimulus),
            shape_ids=settings.shape_ids,
            response_keys=settings.response_keys,
        )

        trigger_runtime.send(settings.triggers.get("exp_onset"))
        StimUnit("instruction", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get("instruction_text")
        ).wait_and_continue(keys=[str(settings.continue_key)])

        all_rows: list[dict] = []
        for plan in plans:
            trigger_runtime.send(settings.triggers.get("block_onset"))
            _show_familiarization(
                plan=plan,
                total_blocks=len(plans),
                win=win,
                kb=kb,
                settings=settings,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
            )
            block = (
                BlockUnit(
                    block_id=plan.block_id,
                    block_idx=plan.block_idx,
                    settings=settings,
                    window=win,
                    keyboard=kb,
                    seed=int(settings.overall_seed) + plan.block_idx,
                )
                .add_condition(list(plan.trials))
                .run_trial(
                    partial(
                        run_trial,
                        stim_bank=stim_bank,
                        trigger_runtime=trigger_runtime,
                        block_id=plan.block_id,
                        block_idx=plan.block_idx,
                    )
                )
            )
            block.to_dict(all_rows)
            trigger_runtime.send(settings.triggers.get("block_end"))

            if plan.block_idx < len(plans) - 1:
                StimUnit("block_break", win, kb, runtime=trigger_runtime).add_stim(
                    stim_bank.get_and_format(
                        "block_break",
                        block_number=plan.block_idx + 1,
                        total_blocks=len(plans),
                    )
                ).wait_and_continue(keys=[str(settings.continue_key)])

        result_path = Path(settings.res_file)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(all_rows).to_csv(result_path, index=False)
        result_path.with_name(f"{result_path.stem}_rlwm_summary.json").write_text(
            json.dumps(summarize_learning(all_rows), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        trigger_runtime.send(settings.triggers.get("good_bye_onset"))
        StimUnit("good_bye", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get("good_bye_text")
        ).wait_and_continue(keys=[str(settings.continue_key)])
        trigger_runtime.send(settings.triggers.get("exp_end"))
        trigger_runtime.close()
        win.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the RLWM set-size learning task.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()
