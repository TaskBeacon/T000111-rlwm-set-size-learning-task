# RLWM Set-Size Learning Task

| Metadata | Value |
|---|---|
| Name | RLWM Set-Size Learning Task |
| Version | 0.1.0 |
| Date Updated | 2026-08-29 |
| PsyFlow Version | 0.3.0 |
| PsychoPy Version | 2025.1+ |
| Modality | Behavioral |
| Language | Chinese |

> TaskBeacon ID: `T000111`  
> Variant: `baseline`  
> Acquisition: `behavior`  
> Language: Chinese  
> Version: `v0.1.0`

## 1. Task Overview

The Reinforcement Learning and Working Memory (RLWM) task measures how concurrent memory load changes deterministic stimulus-action learning. In each independent block, participants learn which of three adjacent keys is correct for each visual stimulus. The number of mappings varies from two to six while stimulus timing, response options, and truthful binary feedback remain constant.

The canonical implementation follows the shared deterministic protocol in Collins (2025), supported by the original RLWM design in Collins and Frank (2012). It uses 18 blocks and 15 iterations per stimulus. Primary outputs are accuracy and response time as functions of set size, stimulus iteration, and delay since the previous presentation of the same stimulus.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

1. Task instructions explain stable within-block mappings, three response keys, and truthful feedback.
2. Each block begins with the complete set of 2-6 colored geometric stimuli for familiarization.
3. Every stimulus is presented 15 times in pseudo-randomly interleaved rounds.
4. A neutral break separates blocks; a new block introduces new stimuli and mappings.

### Trial-Level Flow

| Phase | Duration | Visible content | Response |
|---|---:|---|---|
| Stimulus response | 1.5 s maximum | One centered block-specific colored shape | F, G, or H |
| Feedback | 0.75 s | `正确 +1`, `错误 0`, or `未作答 0` | None |
| Inter-trial interval | 0.5 s | Fixation cross | None |

### Controller Logic

No adaptive controller is used. A subject-seeded block plan fixes each stimulus's correct key before the block begins. Correct keys are sampled independently, so different stimuli may share the same correct key. Feedback is deterministic and does not update the mapping.

### Other logic

The custom schedule is required to preserve stable item-level mappings, equal presentations, stimulus iteration numbers, and local repeat delays. Set-size order is rotated and optionally reversed by participant seed while retaining a low/high interleaving pattern. Trial identity is assigned by PsyFlow.

## 3. Configuration Summary

### a. Subject Info

| Field | Human profile |
|---|---|
| Subject ID | Six-digit integer |
| Seed policy | Stable within participant |
| Language/font | Chinese / SimHei |

### b. Window Settings

| Setting | Value |
|---|---|
| Resolution | 1280 × 720 px |
| Background | White |
| Fullscreen | False by default |
| Monitor geometry | 35.5 cm width, 60 cm distance |

### c. Stimuli

| Component | Implementation |
|---|---|
| Stimulus set | 2-6 circles/polygons/rectangles with block-specific colors |
| Familiarization | All block stimuli in a centered horizontal row |
| Response keys | F, G, H |
| Correct feedback | Green `正确 +1` |
| Incorrect feedback | Red `错误 0` |
| Timeout feedback | Gray `未作答 0` |

### d. Timing

| Parameter | Human | QA/simulation |
|---|---:|---:|
| Blocks | 18 | 5 |
| Set sizes | 2-6 | 2-6 |
| Iterations per stimulus | 15 | 2 |
| Stimulus/response window | 1.5 s | 1.5 s, runtime-scaled |
| Feedback | 0.75 s | 0.75 s, runtime-scaled |
| ITI | 0.5 s | 0.5 s, runtime-scaled |

### Triggers

| Family | Codes |
|---|---|
| Experiment/block lifecycle | 1-4 |
| Stimulus onset by set size | 12-16 |
| F/G/H responses | 21-23 |
| Response timeout | 29 |
| Feedback | 31, 32, 39 |
| ITI/goodbye | 40, 60 |

### Adaptive controller

Not applicable. All mappings and trial orders are precomputed from the participant and block seed.

## 4. Methods (for academic publication)

Participants completed a deterministic instrumental-learning task in which each visual stimulus was associated with one of three adjacent response keys. The experiment comprised 18 independent blocks. Concurrent learning load was manipulated by varying the number of stimuli within a block from two to six. Before each block, the full stimulus set was displayed for familiarization. Each stimulus was then presented 15 times in pseudo-randomly interleaved rounds. Correct response assignments were fixed within a block, generated independently across stimuli, and reset between blocks.

On each trial, a single colored geometric stimulus appeared centrally for up to 1.5 s. Participants responded using F, G, or H. A correct response produced `正确 +1`; an incorrect response produced `错误 0`; omission produced `未作答 0`. Feedback remained visible for 0.75 s, followed by a 0.5 s fixation interval. Trial records included set size, stimulus identity and geometry, correct and chosen actions, iteration, delay since the prior occurrence of that stimulus, reaction time, accuracy, timeout status, and reward.

The human profile includes all five set sizes and 1,035 logical trials. QA and simulation profiles shorten only block and iteration counts while retaining all set-size levels, stage ordering, response semantics, and feedback branches.

### Running the task

```powershell
python main.py human --config config/config.yaml
python main.py qa --config config/config_qa.yaml
python main.py sim --config config/config_scripted_sim.yaml
python main.py sim --config config/config_sampler_sim.yaml
```

### References

- Collins, A. G. E. (2025). A habit and working memory model as an alternative account of human reward-based learning. *Nature Human Behaviour*. https://doi.org/10.1038/s41562-025-02340-0
- Collins, A. G. E., & Frank, M. J. (2012). How much of reinforcement learning is working memory, not reinforcement learning? *European Journal of Neuroscience, 35*, 1024-1035. https://doi.org/10.1111/j.1460-9568.2011.07980.x
- Collins, A. G. E., Brown, J. K., Gold, J. M., Waltz, J. A., & Frank, M. J. (2014). Working memory contributions to reinforcement learning impairments in schizophrenia. *Journal of Neuroscience, 34*, 13747-13756. https://doi.org/10.1523/JNEUROSCI.0989-14.2014
- Collins, A. G. E., Ciullo, B., Frank, M. J., & Badre, D. (2017). Working memory load strengthens reward prediction errors. *Journal of Neuroscience, 37*, 4332-4342. https://doi.org/10.1523/JNEUROSCI.2700-16.2017
