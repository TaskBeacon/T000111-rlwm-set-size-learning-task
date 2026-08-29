# Task Logic Audit

This audit was derived from the user-provided 2025 Nature Human Behaviour article, its Fig. 1 and Methods, and the open 2012 original protocol before the implementation logic was finalized.

## 1. Paradigm Intent

- Task: RLWM Set-Size Learning Task.
- Primary construct: working-memory contributions to deterministic instrumental learning.
- Manipulated factors: number of stable stimulus-action mappings learned concurrently within a block (`n_s = 2, 3, 4, 5, 6`) and local delay between repetitions of the same stimulus.
- Dependent measures: response accuracy and latency by set size and stimulus iteration, repeat delay, error identity/history, and learning curves.
- Key citations: Collins (2025); Collins and Frank (2012); Collins et al. (2014, 2017).

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 18 in the human profile, matching the CF12 dataset count reported by the primary source.
- Trials per block: `set_size × 15`; therefore 30, 45, 60, 75, or 90 logical trials.
- Randomization/counterbalancing: the configured low/high alternating set-size schedule is deterministically rotated and optionally reversed from the participant seed. Each block receives novel shape-color combinations and independently sampled stable correct keys.
- Condition weight policy: `task.condition_weights` is `null`; weighted label generation cannot express block-specific set size, item identity, stable mappings, and repeat number.
- Condition generation method: custom `build_block_plans(...)` in `src/utils.py`.
- Why custom generation is required: each condition must carry an item-level stable shape/color/key mapping across 15 repetitions, with equal item counts and controlled interleaving. Exchangeable label sampling would not preserve these cross-trial constraints.
- Generated condition shape passed to `run_trial.py`: `TrialSpec(block_id, block_idx, set_size, stimulus_id, shape_id, fill_color, correct_key, stimulus_iteration, sequence_index, delay_trials)`.
- Runtime-generated trial values: none in `run_trial.py`. All core factors are generated before `BlockUnit.add_condition(...)`; trial identity alone comes from PsyFlow `next_trial_id()`.

The 18-block schedule contains four blocks each of set sizes 2, 3, and 4, and three each of set sizes 5 and 6. This count distribution is inferred because the primary source reports 18 blocks but not their exact allocation; it retains denser low-load sampling from the original protocol while preserving every set-size level.

### Trial State Machine

1. State name: `stimulus_response`.
   - Onset trigger: set-size-specific stimulus onset (`stimulus_ss2_onset` through `stimulus_ss6_onset`).
   - Stimuli shown: one centered geometric form with its block-specific color.
   - Valid keys: configured adjacent keys F, G, H.
   - Timeout behavior: at 1.5 s, record no response and a zero outcome.
   - Next state: `feedback`.
2. State name: `feedback`.
   - Onset trigger: `feedback_correct`, `feedback_incorrect`, or `feedback_timeout`.
   - Stimuli shown: truthful binary outcome (`正确 +1`, `错误 0`, or `未作答 0`).
   - Valid keys: none.
   - Timeout behavior: automatically advances after 0.75 s.
   - Next state: `inter_trial_interval`.
3. State name: `inter_trial_interval`.
   - Onset trigger: `iti_onset`.
   - Stimuli shown: fixation cross.
   - Valid keys: none.
   - Timeout behavior: automatically advances after 0.5 s.
   - Next state: next interleaved stimulus or block end.

Before the first logical trial of every block, `block_familiarization` shows the full stimulus set until Space, matching the original protocol. Between blocks, a neutral progress/break screen waits for Space.

## 3. Condition Semantics

- Condition ID: `set_size_2`.
  - Participant-facing meaning: learn two arbitrary shape-key mappings concurrently.
  - Concrete stimulus realization: two block-specific colored geometric forms; one appears per trial.
  - Outcome rules: only the preassigned correct key yields `正确 +1`.
- Condition ID: `set_size_3`.
  - Participant-facing meaning: learn three mappings; otherwise identical.
  - Concrete stimulus realization: three distinct forms.
  - Outcome rules: identical deterministic binary rule.
- Condition ID: `set_size_4`.
  - Participant-facing meaning: learn four mappings.
  - Concrete stimulus realization: four distinct forms.
  - Outcome rules: identical.
- Condition ID: `set_size_5`.
  - Participant-facing meaning: learn five mappings.
  - Concrete stimulus realization: five distinct forms.
  - Outcome rules: identical.
- Condition ID: `set_size_6`.
  - Participant-facing meaning: learn six mappings.
  - Concrete stimulus realization: six distinct forms.
  - Outcome rules: identical.

Participant-facing text is defined in `config/*.yaml`. Geometric attributes are precomputed into each condition from cited shape/color logic, then applied through `StimBank.rebuild(...)`. Localizing text requires YAML changes only; internal condition tokens are never displayed.

## 4. Response and Scoring Rules

- Response mapping: press one of F/G/H for the centered stimulus.
- Response key source: `task.response_keys` in config.
- Missing-response policy: a 1.5 s timeout is saved as `timed_out=true`, `reward=0`, and `outcome=timeout`.
- Correctness logic: exact equality between the response key and the block-stable `correct_key` for that stimulus.
- Reward/penalty updates: correct `+1`; incorrect or timeout `0`; no accumulated score is required for future contingencies.
- Running metrics: no learning metric is shown during the task. Saved summaries report trial count, responses, correct count, and accuracy by set size.

## 5. Stimulus Layout Plan

- Screen name: instruction.
  - Stimulus IDs shown together: `instruction_text`.
  - Layout anchors: `[0, 0]`.
  - Size/spacing: 28 px, wrap width 1060 px.
  - Readability/overlap checks: one centered multiline block at 1280×720.
  - Rationale: explains stable mappings and truthful feedback without revealing any mapping.
- Screen name: block familiarization.
  - Stimulus IDs shown together: `familiarization_header` plus 2-6 `stimulus_*` primitives.
  - Layout anchors: header `[0, 220]`; shapes on a centered horizontal row at y=-20.
  - Size/spacing: 170 px center spacing; maximum six-item span 850 px; shape envelope at most 155 px.
  - Readability/overlap checks: at set size 6, outer shapes remain inside ±500 px, leaving >100 px side margins; header remains >160 px above shape centers.
  - Rationale: directly implements whole-set familiarization.
- Screen name: stimulus response.
  - Stimulus IDs shown together: one dynamic `stimulus_*` primitive.
  - Layout anchors: `[0, 0]`.
  - Size/spacing: 140-155 px.
  - Readability/overlap checks: single stimulus; no text overlap.
  - Rationale: isolates arbitrary stimulus-action learning without repeating key reminders.
- Screen name: feedback.
  - Stimulus IDs shown together: exactly one `feedback_*` text.
  - Layout anchors: `[0, 0]`.
  - Size/spacing: 44-48 px.
  - Readability/overlap checks: single outcome label.
  - Rationale: binary truthful feedback from the protocol.

## 6. Trigger Plan

| Event family | Codes | Semantics |
|---|---:|---|
| experiment | 1, 2 | experiment onset/end |
| block | 3, 4 | block onset/end |
| stimulus set size | 12-16 | stimulus onset for set sizes 2-6 |
| response key | 21-23 | F/G/H response events |
| response timeout | 29 | no key before deadline |
| feedback | 31, 32, 39 | correct, incorrect, timeout feedback |
| ITI | 40 | inter-trial fixation onset |
| goodbye | 60 | completion screen onset |

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one mode-aware flow with a small familiarization helper, an explicit block loop, and direct `BlockUnit` execution.
- `utils.py` used: yes.
- Exact purpose: deterministic subject/block seeding, item-level stable mapping creation, interleaved equal-count schedule creation, repeat-delay annotation, and summary computation.
- Custom controller used: no; mappings do not adapt after assignment and feedback is deterministic.
- Legacy/backward-compatibility fallback logic required: no.

## 8. Inference Log

- Decision: use F/G/H as the three adjacent keys.
  - Why inference was required: the papers specify three adjacent keys but not their literal labels.
  - Citation-supported rationale: these keys satisfy the reported physical arrangement.
- Decision: allocate 18 blocks as 4/4/4/3/3 across set sizes 2/3/4/5/6.
  - Why inference was required: the primary source reports 18 CF12 blocks but omits the allocation; the original reports a 19-block distribution weighted toward lower loads.
  - Citation-supported rationale: preserves all five load levels and extra low-load precision while matching 18 total.
- Decision: fixed 15 iterations per stimulus.
  - Why inference was required: shared Methods permits 10-15; original protocol may stop after criterion.
  - Citation-supported rationale: the primary article's GL dataset explicitly uses 15, and its error analysis distinguishes iterations 1-5 from 6+.
- Decision: 0.75 s feedback.
  - Why inference was required: primary Methods gives 0.5-1 s.
  - Citation-supported rationale: midpoint lies inside the direct range.
- Decision: use fixation during the 0.5 s ITI and score timeout as zero.
  - Why inference was required: visual content of ITI and timeout wording are not specified.
  - Citation-supported rationale: neutral fixation adds no information; no response cannot earn the deterministic +1 outcome.

## Contract Note

- Participant-facing labels, instructions, and feedback are config-defined.
- `src/run_trial.py` only sequences cited states and consumes precomputed trial factors.

