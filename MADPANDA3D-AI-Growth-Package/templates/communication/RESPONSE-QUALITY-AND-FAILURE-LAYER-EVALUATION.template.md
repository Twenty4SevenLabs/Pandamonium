# RESPONSE-QUALITY-AND-FAILURE-LAYER-EVALUATION

## Evaluation Contract

| Field | Value | Evidence basis | Checked | Owner |
| --- | --- | --- | --- | --- |
| Evaluation purpose / accountable evaluation owner |  |  |  |  |
| Workflow / use / consequence |  |  |  |  |
| Audience / channel / accessibility |  |  |  |  |
| Exact input / response safe references |  |  |  |  |
| Expected / prohibited behavior |  |  |  |  |
| Source of truth / accepted COM artifact references |  |  |  |  |
| Rubric version / frozen anchors |  |  |  |  |
| Applicable dimensions / critical-gate rule |  |  |  |  |
| Material-disagreement rule |  |  |  |  |
| Privacy / rights / retention |  |  |  |  |
| Task-outcome evidence rule |  |  |  |  |
| Scoring / repair-test authority and prohibited actions |  |  |  |  |
| Independent reviewers / Evaluation-integrity / Repair-diagnosis owners |  |  |  |  |

## Evaluation Cases

| EVAL-## | Order | Workflow / consequence | Input / response safe refs | Expected behavior | Prohibited behavior | Task-outcome state / evidence | Applicable / critical dimensions | Privacy / rights state | Owner | Prerequisite IDs | State | Maximum conclusion | Task or defer reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | `SUCCEEDED` / `FAILED` / `UNKNOWN` / `NOT RUN` |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT REQUIRED` / `NOT RUN` |  |  |

## Canonical Dimensions and Anchors

| DIM-## | Dimension | Observable 0 anchor | Observable 1 anchor | Observable 2 anchor | Observable 3 anchor | Critical when | NOT APPLICABLE rule | NOT SCORED rule | Owner / version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DIM-01` | Goal and audience fit |  |  |  |  |  |  |  |  |
| `DIM-02` | Truth, evidence, and uncertainty |  |  |  |  |  |  |  |  |
| `DIM-03` | Context uptake and clarification |  |  |  |  |  |  |  |  |
| `DIM-04` | Language, tone, channel, and accessibility |  |  |  |  |  |  |  |  |
| `DIM-05` | Expression, disagreement, and repair |  |  |  |  |  |  |  |  |
| `DIM-06` | Privacy, authority, and escalation |  |  |  |  |  |  |  |  |

`0` through `3` are observable case scores, not percentages or model grades.
`NOT APPLICABLE` means the frozen contract excludes the dimension for this
case. `NOT SCORED` means required evidence or an anchor is missing and blocks
that case. Task outcome remains separate. A critical `0` forces case
disposition `REJECT`; no total or average can override it.

## Independent Scores

| SCR-## | EVAL-## | DIM-## | Reviewer | Independence checked | Applicability / criticality | Exact anchor | Score | Evidence safe refs | Reason | State | Maximum conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  | `0` / `1` / `2` / `3` / `NOT APPLICABLE` / `NOT SCORED` |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT RUN` |  |

## Agreement and Case Disposition

| AGR-## | EVAL-## / DIM-## | Reviewer score pair | Material under frozen rule | Evidence / applicability / criticality / anchor disagreement | Disposition | Rubric repair / owner decision | Old / new rubric versions | Rescore refs | Case disposition | Owner | State | Maximum conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | `YES` / `NO` / `UNKNOWN` |  |  |  |  |  | `USABLE` / `REPAIR` / `REJECT` / `UNKNOWN` |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT RUN` |  |

## Failure-Layer Hypotheses and Repair Tests

| FLR-## | EVAL-## / defect | Observable defect evidence | Candidate layer | Competing layers / evidence gaps | Earliest supported boundary | Prohibited cause claim | Smallest single-variable repair test | Expected discriminating result | Owner / authority | Prerequisite IDs | State | Maximum conclusion | Task or defer reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | `CONTRACT` / `INPUT-CONTEXT` / `RETRIEVAL-KNOWLEDGE` / `INSTRUCTION-POLICY` / `TOOL-ACTION` / `GENERATION` / `CHANNEL-PRESENTATION` / `REVIEW-HANDOFF` |  |  |  |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT REQUIRED` / `NOT RUN` |  |  |

## Reviews and Readiness

- Declared evaluation order:
- Global contract blocker:
- First failed or unknown required row:
- Case-local dependent rows marked `NOT RUN`:
- Independent cases and scores preserved:
- Critical-zero dispositions:
- Material scoring disagreements and dispositions:
- First next-owner task:
- Deferred blockers and reasons:
- Unresolved competing failure layers:
- Evaluation-integrity review owner:
- Evaluation-integrity review: `PENDING` / `PASS` / `REPAIR`
- Repair-diagnosis review owner:
- Repair-diagnosis review: `PENDING` / `PASS` / `REPAIR`
- `READY FOR COM-10: YES` / `READY FOR COM-10: NO`

`READY FOR COM-10: YES` requires a complete shared contract; at least two
rights-cleared fictional cases; frozen dimensions, anchors, critical gates,
and materiality rule; two independent scores per applicable dimension; task
outcome kept separate; every critical `0` forced to `REJECT`; every material
disagreement disposed and rescored when the rubric changed; each required
failure-layer row bounded to evidence and a smallest repair test; no invented
score, cause, success, approval, or general-quality claim; and both reviews
`PASS`. A correctly rejected bad response may still support readiness. A
task-outcome state of `UNKNOWN` or `NOT RUN` does not itself block readiness
when its evidence and maximum conclusion are complete; missing required
task-outcome evidence does. A
missing shared contract field stops all scoring. A case-local missing input,
score, evidence item, owner, or prerequisite makes that row `UNKNOWN` and its
dependents `NOT RUN`; independent cases remain evaluated, both reviews are
`REPAIR`, and readiness is `NO`. This artifact authorizes no send, contact,
tool action, record change, prompt or model deployment, fine-tuning, purchase,
or claim of general response quality.
