# Task Plot Review

Status: PASS on generation round 1; no regeneration required.

## Evidence Match

- Task identity and construct match the canonical task.
- Representative rows correctly cover low, middle, and high load (`n=2`, `n=4`, `n=6`), with a note listing all implemented set sizes 2-6.
- Familiarization screens contain exactly 2, 4, and 6 shapes in their corresponding rows.
- Trial order is correct: Familiarize -> Choose -> Feedback -> ITI.
- Choose contains exactly one shape and the configured F/G/H response keys.
- Timing labels match the canonical config: 1.5 s maximum response, 0.75 s feedback, 0.5 s ITI.
- Feedback shows only the deterministic `CORRECT +1` and `INCORRECT 0` branches.

## Visual Quality

- Text is sharp and readable at normal preview size.
- Screen boxes, phase labels, timing captions, arrows, and row separators do not overlap.
- Shape scale remains consistent; set-size differences are represented by count rather than size.
- No garbled labels, unsupported stimuli, people, devices, decorative scenery, or image-model branding are present.
- Fixed centered title, `Construct:` subtitle, and borderless top-right TaskBeacon lockup are present and do not overlap the timeline.
- The raw image retains the blank header band before fixed post-processing.

## README Embed

- `README.md` begins section `## 2. Task Flow` with `![Task Flow](task_flow.png)`.
- Final image is saved as `task_flow.png` at the task root.
