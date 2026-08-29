# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `set_sizes` | `task.conditions`, `task.set_size_schedule` | 2, 3, 4, 5, 6 | `PAPER_PRIMARY`; `COLLINS_FRANK_2012` | Primary Methods, Shared: set size varies from two to six; original Methods reports the same five levels. | `direct` | Core working-memory load manipulation. |
| `total_blocks` | `task.total_blocks` | 18 | `PAPER_PRIMARY` | Primary Methods, dataset CF12: 18 blocks in the reanalysed dataset. | `direct` | Human profile only; QA/sim use five mechanism-complete blocks. |
| `block_set_size_counts` | `task.set_size_schedule` | n=2/3/4 each 4 blocks; n=5/6 each 3 blocks | `PAPER_PRIMARY`; `COLLINS_FRANK_2012` | Primary gives 18 total blocks; original protocol reports more low-load blocks and three blocks for each higher load. | `inferred` | Preserves 18 blocks while retaining denser sampling at lower loads. Schedule alternates low/high loads and is subject-rotated/reversed. |
| `iterations_per_stimulus` | `task.iterations_per_stimulus` | 15 | `PAPER_PRIMARY` | Primary Methods: stimuli repeat 10-15 times; dataset GL used 15 iterations per stimulus. | `adapted` | Fixed 15 iterations avoid performance-contingent session length and preserve the primary article's late-learning range. |
| `stimulus_order` | `src.utils._trial_order` | interleaved shuffled rounds | `PAPER_PRIMARY` | Primary Methods: pseudo-random interleaving controls repeat delay with a close-to-uniform span from 1 to 2n-1. | `adapted` | Independent shuffled rounds keep every stimulus equally sampled and repeat delays bounded near the cited span. |
| `block_familiarization` | `main._show_familiarization` | whole set shown until Space | `COLLINS_FRANK_2012` | Original Methods: the complete stimulus set is shown at the start of each block for familiarization. | `direct` | Participant controls familiarization duration. |
| `actions` | `task.response_keys` | F, G, H | `PAPER_PRIMARY`; `COLLINS_FRANK_2012` | Primary Methods: three adjacent key presses; original protocol likewise uses three responses. | `adapted` | Exact physical keys were not reported; F/G/H are adjacent and centrally located. |
| `mapping_stability` | block plans | one deterministic correct key per stimulus within each block | `PAPER_PRIMARY` | Primary Fig. 1a and Methods: stable stimulus-action associations with truthful deterministic binary feedback. | `direct` | New mapping generated for every independent block. |
| `mapping_independence` | `src.utils.build_block_plans` | key sampled independently per stimulus; repeats allowed | `COLLINS_FRANK_2012` | Original Methods: one stimulus's action is not informative about another; correct keys need not be distinct. | `direct` | Prevents elimination-based inference. |
| `response_window_s` | `timing.response_window_s` | 1.5 s | `PAPER_PRIMARY` | Primary Methods: stimuli typically shown for 1.5 s while participants respond. | `direct` | Response terminates the window; feedback follows immediately. |
| `feedback_duration_s` | `timing.feedback_duration_s` | 0.75 s | `PAPER_PRIMARY` | Primary Methods: feedback interval is 0.5-1 s. | `adapted` | Midpoint of the reported range. |
| `iti_duration_s` | `timing.iti_duration_s` | 0.5 s | `PAPER_PRIMARY` | Primary Methods: inter-trial interval typically 0.5 s. | `direct` | Fixation cross is shown during the interval. |
| `feedback_values` | `stimuli.feedback_*` | correct +1; incorrect/timeout 0 | `PAPER_PRIMARY` | Primary Fig. 1a and Methods: correct or +1 versus incorrect or 0, truthfully delivered. | `direct` | Timeout outcome is conservatively scored as 0. |
| `stimulus_family` | `task.shape_ids`, `stimuli.stimulus_*` | six geometric shapes with block-specific colors | `PAPER_PRIMARY` | Primary Fig. 1a depicts distinguishable shapes and colored forms as the block stimuli. | `adapted` | PsychoPy primitives reproduce the cited visual logic without external assets. |
| `participant_language` | `task.language`, `stimuli.*.font` | Chinese, SimHei | TaskBeacon policy | User-facing default and repository localization policy. | `inferred` | Scientific variables and physical keys remain language-neutral. |
| `trigger_codes` | `triggers.map` | 1-60 by event family | TaskBeacon policy | Hardware codes are not specified in the literature. | `inferred` | Codes separate experiment, block, set-size onset, key, feedback, timeout, and ITI events. |

