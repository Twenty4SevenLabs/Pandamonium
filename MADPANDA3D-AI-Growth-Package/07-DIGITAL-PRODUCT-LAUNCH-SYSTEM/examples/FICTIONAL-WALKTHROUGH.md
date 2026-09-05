# Fictional End-to-End Walkthrough

**Everything below is fictional.** Names, evidence, thresholds, prices, channels, and results are invented only to show how the files connect. They are not customer results, recommendations, benchmarks, or promises.

## Scenario

A fictional solo consultant named Rowan has a repeatable method for helping local service businesses organize customer-onboarding handoffs. Rowan wants to test a small digital toolkit, not sell consulting through this example.

## Play 0 — Capability and authority

Rowan creates a private work folder, copies `STATUS.template.md` to `STATUS.md`, records the package version and exact archive SHA-256 as `MATCH`, and copies every `assets/` file. The purchased package remains unchanged.

When Rowan pauses halfway through Play 2, the agent records the current action, last completed action, evidence artifact, and next checkpoint. In a fresh conversation, it preserves the existing `STATUS.md`, verifies the package hash and prior artifacts, and resumes Play 2 rather than restarting Play 0.

Three fail-closed examples are tested separately: a blank/wrong package hash leaves the workspace unchanged; a missing Play 1 artifact sets Play 1 to `REWRITE` and later `PASS` plays to `BLOCKED` while preserving evidence; contradictory progress with no deterministic earliest invalid artifact stops for Rowan's reconciliation.

The capability map records:

- available: manual web research, documents, spreadsheets, a test storefront, and one owner-controlled social account;
- unavailable: automated delivery and support inbox integration;
- budget: zero until the owner changes it explicitly;
- human approval: required for publication, messages, account changes, spending, and real transactions;
- stop: no live checkout until delivery/support testing passes.

**Gate:** pass. The missing delivery capability has a documented manual test fallback, but it blocks live activation.

## Play 1 — Buyer problem

Rowan compares three ideas and selects this hypothesis:

> For small local-service teams onboarding a new customer, unclear ownership and scattered intake details cause repeated follow-up because current notes do not define the handoffs.

This is labeled an assumption. Rowan excludes regulated advice, CRM implementation, and any use of prior client records.

**Artifact:** `BUYER-PROBLEM-BRIEF.md`.

## Play 2 — Evidence and offer

Rowan records public sources and five voluntary conversations. The conversations are summarized without names or message bodies. Evidence suggests handoff confusion exists; it does not prove willingness to pay.

Fictional offer:

> A self-guided onboarding-handoff toolkit that helps a small team name the owner, required input, review point, and completion signal for one onboarding workflow.

Unsupported claims such as “save ten hours” and “never lose a customer” are rejected.

**Validation test:** share one useful blank handoff map in approved contexts and ask five target users to complete it. Pass/revise/stop rules are declared before outreach.

## Play 3 — Product design

The fictional product contains:

- `START.md`;
- one handoff-map worksheet;
- one approval/stop checklist;
- one fictional completed example;
- one use-rights and privacy note.

Completion outcome: a buyer can document one onboarding workflow with an owner, inputs, handoffs, review, and measurable completion signal.

## Play 4 — Clean build

Rowan builds in an empty allowlisted directory. Private interview notes remain outside it. The manifest records file jobs, sizes, and hashes. `SHA256SUMS.txt` is generated after the manifest. The ZIP extracts into one root and contains no executable files.

## Play 5 — Independent QA

A fictional independent reviewer receives the exact archive and hash. The reviewer finds that the example contains an unlabeled invented company name and that the start file does not tell the buyer to copy the worksheet.

Verdict: `REWRITE`.

Rowan labels the example fictional, adds the copy instruction, creates a new candidate hash, and requests a full retest. The second fictional review returns `PASS`.

## Play 6 — Buyer path

Rowan maps landing, test checkout, paid, failed, duplicate, delivery, expired-link, support, refund, and dispute states. The fictional policies are declared before testing:

- currency and price: chosen by Rowan, not this package;
- delivery-link expiry: chosen after a security review;
- support target and refund window: chosen by Rowan and reviewed for applicable obligations;
- no third-party advertising tracker.

A test purchase produces one test order and one delivery. A duplicate event produces no second delivery. Live checkout stays closed because the support inbox still lacks acceptance evidence.

A different fictional reviewer receives the exact `BUYER-PATH-PLAN.md`, package hash, readiness record, and sandbox evidence after the plan is created. Because support remains untested, the reviewer returns `BLOCKED`; the guide does not self-certify or proceed to publication. After the support test passes and the plan is versioned, a new independent review returns `PASS`. Checkout still remains closed because Play 6 never authorizes activation.

## Play 7 — Organic launch

Rowan approves one exact owned account and checks all existing published and scheduled posts before planning new capacity. Three fictional briefs teach the handoff map, approval rule, and QA lesson. No cold messages or repeated comments are used. Drafts are not counted as published.

Before any publication or activation, Rowan opens Play 8 only to write, date, and freeze `PRELAUNCH-DECISION-RULES.md`. Rowan then saves, verifies, and checkpoints the exact `ORGANIC-LAUNCH-PLAN.md` and marks Play 7 `PASS`. Only then can Rowan review an exact activation or publication action. The measurement interval remains `NOT_STARTED` until the declared qualified-visit event is later verified.

## Play 8 — Predeclared evidence loop

Before launch, Rowan writes fictional rules:

- interval: 30 days from the first verified qualified visit, allowing a useful pre-sale/zero-order path;
- qualified visit: a non-test product-page session carrying a valid first-party campaign tag;
- visit floor, order signal, refund limit, support target, and recurring-defect definition: selected by Rowan from business economics and risk tolerance;
- low reach: revise distribution;
- sufficient reach but weak completion signal: revise the offer once;
- operational failure: stop and fix before expansion.

A paid order arrives before the declared qualified-visit event. The interval remains `NOT_STARTED`; Rowan does not switch the event. It starts only when the declared qualified visit is authoritatively verified and timestamped.

The example deliberately provides no universal numbers. Before seeing results, Rowan declares an integer recurrence threshold for one fulfillment-defect class. If cohort paid orders remain zero, refund rate is `NOT_APPLICABLE`; visits, handoffs, readiness, and objections still support a distribution/offer decision. For later orders, any partially or fully refunded order counts once in `cohort_unique_refunded_orders_snapshot`, actual refunded cash stays in `refund_amount_flow`, and settled dispute losses—not open snapshots—enter `net_amount_flow`. Rowan changes one variable per review cycle.

For the fictional accounting test, non-overlapping `PERIOD_FLOW` rows record cash movements and new unique orders. A partial refund in week two and another refund on the same order in week three create two refund cash movements but one refunded order in that cohort's latest `COHORT_SNAPSHOT`. An open dispute appears only in the week-end snapshot; after loss settlement it leaves the next snapshot and enters settled-loss flow exactly once. Defects are logged by class: two `EXPIRED_LINK` records plus one `WRONG_FILE` do not meet a threshold of three; a third `EXPIRED_LINK` does.

## Final lesson

The plays produce connected artifacts, but they do not remove owner decisions or guarantee a launch result. A structurally valid package can still be blocked by rights, support, delivery, checkout, account authority, or independent-QA evidence.
