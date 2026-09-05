# Product QA Rubric

Score each row `PASS`, `FAIL`, or `NOT_APPLICABLE`. A critical failure forces `REWRITE` or `BLOCKED`.

| Area | Severity if failed | Check | Evidence |
|---|---|---|---|
| Candidate identity | Critical | Report records exact archive name and SHA-256 hash | |
| Clean extraction | Critical | Archive extracts into an empty folder without traversal or unexpected executables | |
| Manifest | Critical | Manifest parses and inventory/hashes agree with actual files | |
| Start flow | Critical | A new buyer/agent can identify and perform the first action | |
| Promise match | Critical | Package can produce every advertised artifact/outcome | |
| Truthfulness | Critical | No guaranteed sales, fabricated proof, false scarcity, or unshipped capability | |
| Privacy | Critical | No credentials, customer data, private client work, internal IDs, or internal-only paths | |
| Rights | Critical | Source ownership and buyer use rights are stated; no copied competitor material | |
| Commercial outputs | Critical | Buyer can distinguish original outputs they may sell from package/third-party material they may not redistribute | |
| Provenance | Critical | Every substantive and generated file class maps to an original rewrite, owned source class, public source, or deterministic generation method | |
| Action authority | Critical | Spend, publish, send, account changes, and real transactions require human approval | |
| Read-only package | Major | Start flow copies status/templates to a separate private work folder and leaves the purchased package unchanged | |
| Evidence discipline | Major | Facts, inferences, assumptions, and decisions are separated | |
| Play structure | Major | Every play has objective, inputs, capability/manual fallback, actions, artifact, criteria, stops, next play | |
| Resume behavior | Major | New identity is initialized; blank/mismatch stops without mutation; invalid artifacts trigger earliest-safe rewind/downstream blocking; contradictions stop | |
| Buyer-path independence | Critical | Play 6 creates a separate exact-plan/package review and cannot self-certify without an independent `PASS` | |
| Portability | Major | Vendor-neutral capabilities and manual fallbacks are used where practical | |
| File validity | Major | JSON/CSV parse; Markdown links and filenames resolve | |
| Accessibility | Major | Headings, tables, language, and nonvisual meaning are usable | |
| Buyer effort | Major | Package asks focused questions and avoids unnecessary reading/work | |
| Failure handling | Major | Stop conditions name evidence and smallest next action | |
| Support boundary | Major | Help path, exclusions, dependencies, and limitations are clear | |
| Versioning | Major | Product version is consistent and edits require a new candidate/retest | |
| Policy portability | Major | Example thresholds, processor fields, delivery expiry, support targets, and refund assumptions are buyer-declared or clearly labeled examples | |
| Zero-order evidence | Major | Pre-sale/zero-order periods remain measurable and order-dependent rates become `NOT_APPLICABLE`, not misleading zeroes | |
| Prelaunch/activation order | Critical | Play 6 cannot activate; Play 7 saves/verifies/checkpoints its plan and frozen rules before external action; Play 8 verifies only the declared event | |
| Flow/cohort accounting | Critical | Non-overlapping period flows, cohort snapshots, late/partial refunds, open/settled disputes, unique orders, and net cannot be double-counted | |
| Defect recurrence | Critical | Recurrence counts one stable defect class inside the frozen scope; mixed classes never combine | |
| Polish | Minor | Spelling, formatting, examples, and terminology are consistent | |

## Verdict rules

- `PASS`: every critical row passes; no unresolved major defect prevents the promised outcome.
- `REWRITE`: defects are correctable within the approved product scope.
- `BLOCKED`: required evidence, rights, capability, independent review, or owner decision is unavailable.

## Defect format

| ID | Severity | Path/step | Observed | Expected | Fix owner | Retest |
|---|---|---|---|---|---|---|
