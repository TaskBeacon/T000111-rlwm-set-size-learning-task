Use case: infographic-diagram
Asset type: TaskBeacon task flow diagram
Primary request: Create a clean, publication-ready task flow diagram as a timeline collection for the behavioral task described below.

Task: RLWM Set-Size Learning Task
Construct: reinforcement learning / working memory
Rows/conditions:
- Set size 2: low load; familiarization contains exactly 2 distinct colored geometric shapes.
- Set size 4: middle load; familiarization contains exactly 4 distinct colored geometric shapes.
- Set size 6: high load; familiarization contains exactly 6 distinct colored geometric shapes.
- Add one compact note outside the screen boxes: `Set sizes: 2, 3, 4, 5, 6`.

Timeline phases:
- Set size 2: Familiarize (self-paced; exactly 2 colored shapes) -> Choose (1.5 s max; one centered colored shape; F G H response) -> Feedback (0.75 s; CORRECT +1 or INCORRECT 0) -> ITI (0.5 s; centered +)
- Set size 4: Familiarize (self-paced; exactly 4 colored shapes) -> Choose (1.5 s max; one centered colored shape; F G H response) -> Feedback (0.75 s; CORRECT +1 or INCORRECT 0) -> ITI (0.5 s; centered +)
- Set size 6: Familiarize (self-paced; exactly 6 colored shapes) -> Choose (1.5 s max; one centered colored shape; F G H response) -> Feedback (0.75 s; CORRECT +1 or INCORRECT 0) -> ITI (0.5 s; centered +)

Visual requirements:
- White background, landscape orientation, crisp dark text, restrained condition accent colors.
- One horizontal row per condition or representative trial type.
- Each row contains 3-7 participant-screen snapshots connected by a subtle arrow.
- Each screen snapshot shows the visible stimulus or feedback, not internal variable names.
- Use gray participant-screen boxes, thin black arrows, consistent row spacing, and subtle row separators.
- Place timing labels under each screen in compact text.
- Place condition labels at the left of each row.
- Use short labels only; avoid paragraphs inside the image.
- Make all text legible at normal document preview size.
- Leave a clean blank header band across the top 15-18% of the image. This band is reserved for a fixed title, `Construct: ...` subtitle, and TaskBeacon logo lockup that will be added after generation.
- Keep geometric stimulus size identical across rows. Only the number shown on Familiarize differs.

Accuracy constraints:
- Do not invent phases, stimuli, condition names, keys, rewards, or timings.
- Do not add people, lab equipment, decorative scenes, logos, or unrelated icons.
- Do not draw the task title, construct subtitle, any logo, watermark, brand mark, or `TaskBeacon` text inside the generated image.
- Draw only the timeline content below the blank header band.
- If a detail is unknown, omit it rather than guessing.
- Preserve these exact terms where used: Set size 2, Set size 4, Set size 6, Familiarize, Choose, Feedback, ITI, F, G, H, CORRECT +1, INCORRECT 0, 1.5 s max, 0.75 s, 0.5 s, Set sizes: 2, 3, 4, 5, 6
- Familiarize must show exactly 2, 4, and 6 colored geometric shapes in the corresponding rows.
- Choose must show exactly one colored geometric shape.
- Do not show probabilistic feedback, coins, money, score bars, cues, anticipation, choice cards, or a second decision.

Style:
TaskBeacon scientific infographic style: clean vector-like raster image, organized spacing, gray screen boxes, restrained color accents, and a blank header-safe area.

Collapse equivalent conditions into representative rows and show variants as small parenthetical notes in the row label.
