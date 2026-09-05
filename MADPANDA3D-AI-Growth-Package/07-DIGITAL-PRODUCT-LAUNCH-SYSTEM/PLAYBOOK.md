# Product 01 Playbook

Run the plays in order. Do not skip a failed gate by rewriting the status as complete.

## Operating protocol

1. Create a private working folder beside this package, not inside the original package.
2. For a new workspace, copy `STATUS.template.md` and initialize its package version and exact archive SHA-256 before Play 0. For an existing workspace, do not mutate it until the resume integrity protocol below passes. Copy only missing editable files from `assets/` after identity validation. Treat the purchased package as read-only.
3. Ask one focused question at a time unless the human asks for a batch.
4. Distinguish four labels in every decision record:
   - **Evidence:** a verifiable source or observed result.
   - **Inference:** a reasoned interpretation of evidence.
   - **Assumption:** an unverified belief that still needs a test.
   - **Decision:** an explicit choice by the human owner.
5. Save sources with title, publisher, URL, publication date when available, retrieval date, and the exact fact supported.
6. Never manufacture testimonials, buyers, scarcity, outcomes, citations, or research.
7. Before any external write, show the exact destination, content or payload, cost, reversibility, and proof that will confirm success. Wait for explicit human approval.
8. Checkpoint `STATUS.md` after each completed action and before any external approval or stop. After each play, run its success criteria, verify the produced artifact, and identify the next smallest action.

## Resume integrity protocol

1. If package version or archive SHA-256 is blank or differs from the reference package, stop without changing status, artifacts, or editable copies. The owner must choose the recorded package or a separate reviewed migration.
2. For each play marked `PASS`, verify its named artifact exists and still passes its gate.
3. If one or more completed artifacts are missing or invalid, preserve all evidence, select the earliest producing play, set it to `REWRITE`, set every later `PASS` play to `BLOCKED`, and resume at the first action that recreates/revalidates that artifact.
4. If current play/action, artifact evidence, gate states, and next action contradict one another without a deterministic earliest invalid artifact, stop without mutation and request owner reconciliation.
5. Never restart Play 0 merely because the conversation is fresh; never overwrite edited templates or an existing `STATUS.md`.

## Play sequence

| Play | Exact file | Purpose | Primary artifact | Gate |
|---|---|---|---|---|
| 0 | `plays/00-agent-and-tool-intake.md` | Inventory the human, agent, tools, permissions, and risks | `AGENT-CAPABILITY-MAP.md` | Real capabilities and approval boundaries documented |
| 1 | `plays/01-extract-buyer-problem.md` | Extract a narrow buyer and costly problem from the owner's experience | `BUYER-PROBLEM-BRIEF.md` | Buyer, problem, evidence, exclusions, and access are specific |
| 2 | `plays/02-validate-demand-and-offer.md` | Validate demand and shape a supportable offer | `OFFER-EVIDENCE-PACKET.md` | Evidence supports the problem; claims and test are bounded |
| 3 | `plays/03-design-the-product.md` | Design the smallest useful product | `PRODUCT-BRIEF.md` | Outcome, contents, rights, exclusions, and acceptance are testable |
| 4 | `plays/04-build-the-package.md` | Build a complete, versioned package | Customer package + manifest | Every promised item exists and opens |
| 5 | `plays/05-run-product-qa.md` | Run independent product QA | `PRODUCT-QA-REPORT.md` | Pass, rewrite, or blocked verdict with evidence |
| 6 | `plays/06-prepare-the-buyer-path.md` | Prepare and independently review the buyer path | `BUYER-PATH-PLAN.md` + `BUYER-PATH-QA-REPORT.md` | Independent verdict is `PASS` for the exact plan/package and tested states |
| 7 | `plays/07-build-the-organic-launch.md` | Build the organic launch | `ORGANIC-LAUNCH-PLAN.md` | Useful drafts, approved channels, tags, cadence, and measurement are ready |
| 8 | `plays/08-run-the-30-day-loop.md` | Run the evidence loop | Scorecard + decision record | Evidence is recorded and the predeclared end gate is applied honestly |

## Global stop conditions

Stop and ask for the smallest owner decision if any of these applies:

- The buyer, problem, promise, price, or use rights are still ambiguous.
- A claim cannot be traced to evidence or directly demonstrated.
- Source material ownership is unknown.
- The proposed product contains credentials, customer data, private client work, internal account identifiers, or licensed material that cannot be redistributed.
- The workflow requests spending, publication, messaging, an account change, or a real transaction without explicit approval.
- Checkout, delivery, support, refund, or privacy behavior cannot be tested.
- Independent QA finds a critical defect.

## Definition of ready to launch

A product is launch-ready only when:

- the exact versioned package passes QA;
- the exact buyer-path plan passes a separate independent review after it is created;
- the landing page describes that exact package and no unshipped feature;
- the price, currency, product, and checkout object agree;
- successful payment, failed payment, duplicate/replayed event, one-time delivery, delivery-link expiry, support, and refund flows have been tested in a safe environment using buyer-defined policies;
- support ownership and response expectations are real;
- organic channels and accounts are explicitly approved;
- measurement can distinguish visits, checkout handoffs, paid orders, fees, refunds, disputes, and net revenue without exposing personal data.
