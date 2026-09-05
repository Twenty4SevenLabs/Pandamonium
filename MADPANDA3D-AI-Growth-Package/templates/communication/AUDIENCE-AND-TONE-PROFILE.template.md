# COM-02 Audience-and-Tone Profile

- Workflow: `[name]`
- Communication-contract path/version: `[COM-01 artifact and version]`
- Workflow owner: `[name or role]`
- Privacy reviewer: `[name or role]`
- Recipient role: `[role in this workflow]`
- Channel: `[channel]`
- Output class: `[internal / draft-only / approval-ready / other]`
- Profile status: `PENDING OWNER AND PRIVACY REVIEW`
- Checked at: `YYYY-MM-DD HH:MM TZ`
- Next review trigger/date: `[event or date]`

## Purpose Boundary

- Response decision this profile improves: `[one decision]`
- Permitted use: `[single workflow and output]`
- Prohibited use: `[decisions or contexts that may not consume it]`
- Minimum-data test: `[why each retained field is necessary]`

## Audience Task Context

| Field | Value | Evidence state | Source owner | Checked | Allowed use | Expiry or review trigger |
| --- | --- | --- | --- | --- | --- | --- |
| Current goal | `[value or UNKNOWN]` | `[state]` | `[owner]` | `[date]` | `[use]` | `[trigger]` |
| Next decision | `[value or UNKNOWN]` | `[state]` | `[owner]` | `[date]` | `[use]` | `[trigger]` |
| Relationship/role | `[value or UNKNOWN]` | `[state]` | `[owner]` | `[date]` | `[use]` | `[trigger]` |
| Time/channel constraint | `[value or UNKNOWN]` | `[state]` | `[owner]` | `[date]` | `[use]` | `[trigger]` |
| Terminology to define | `[value or UNKNOWN]` | `[state]` | `[owner]` | `[date]` | `[use]` | `[trigger]` |

Allowed evidence states: `PERSON-STATED`, `OBSERVED-CONTEXT`,
`CONSENTED-HISTORY`, `INFERENCE`, `ASSUMPTION`, `UNKNOWN`. Keep
`RECOMMENDATION` separate.

## Presentation Preferences

| Preference | Value | Evidence state | Scope | Checked | Expiry/review | Fallback if unknown |
| --- | --- | --- | --- | --- | --- | --- |
| Language | `[value]` | `[state]` | `[scope]` | `[date]` | `[trigger]` | `[clear default]` |
| Format | `[value]` | `[state]` | `[scope]` | `[date]` | `[trigger]` | `[clear default]` |
| Accessibility | `[value]` | `[state]` | `[scope]` | `[date]` | `[trigger]` | `[ask or supported default]` |
| Tone | `[value]` | `[state]` | `[scope]` | `[date]` | `[trigger]` | `[neutral direct default]` |
| Review/readback | `[value]` | `[state]` | `[scope]` | `[date]` | `[trigger]` | `[owner review]` |

Preferences may alter presentation only. They may not alter facts, evidence,
warnings, authority, approval, or escalation.

## Retained-Data Controls

| Field/data class | Purpose | Approved basis | Access owner | Sensitivity | Storage reference | Checked | Review trigger | Retention/expiry | Correction/deletion path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `[field]` | `[purpose]` | `[approved basis]` | `[owner]` | `[class]` | `[approved opaque reference]` | `[date]` | `[trigger]` | `[rule]` | `[path]` |

## Protected Unknowns and Removed Fields

| Field or proposed inference | State | Reason not used | Required reviewer/action |
| --- | --- | --- | --- |
| `[field]` | `UNKNOWN / REMOVED / CONFLICT` | `[unnecessary, unsupported, expired, disputed, or sensitive]` | `[review or none]` |

Do not infer demographic traits, health, disability, emotion, personality,
literacy, culture, religion, politics, gender, financial state, or intent from
indirect signals.

## Test Record

| Test ID | Case | Expected behavior | Result | Evidence/reviewer/date |
| --- | --- | --- | --- | --- |
| `COM02-T01` | Stated preference | Shapes presentation only | `PASS / FAIL / UNKNOWN` | `[record]` |
| `COM02-T02` | Expired preference | Returns to UNKNOWN | `PASS / FAIL / UNKNOWN` | `[record]` |
| `COM02-T03` | Conflicting preference | Stops for review | `PASS / FAIL / UNKNOWN` | `[record]` |
| `COM02-T04` | Unsupported sensitive inference | Removes field and stops if consequential | `PASS / FAIL / UNKNOWN` | `[record]` |

## Approval and Revision

- Workflow owner decision: `PENDING`
- Privacy reviewer decision: `PENDING`
- Approved profile version: `PENDING`
- Approval evidence: `PENDING`
- Revision/change reason: `[record]`
- Fields passed to COM-03: `[approved list only]`
