# Play 6 — Prepare the Buyer Path

## Objective

Make the path from first visit through payment, delivery, support, refund, and update accurate and testable.

## Required inputs

- QA-passed archive and hash
- Approved offer, price, currency, support path, refund policy, privacy notice, and terms
- Checkout/delivery capabilities or documented manual fallbacks
- A private working copy of `assets/launch-readiness-checklist.md`

## Tool capability needed

- **Needed:** document creation and storefront/checkout inspection
- **Needed for an independent verdict:** a reviewer who did not build the buyer path
- **Helpful:** sandbox payment, delivery email, signed-link, analytics, and support-thread testing
- **Manual fallback:** keep checkout closed and document each missing acceptance test; use a human-controlled test inbox and provider test mode when available. If no independent reviewer is available, the plan may be drafted but its gate remains `BLOCKED`.

## Ordered actions

1. Map every state: landing page, checkout handoff, paid, delayed payment, failed payment, duplicate/replayed event, delivery, expired link, support, refund, dispute, and update.
2. Ensure landing copy names the exact product/version, buyer, outcome, contents, price/currency, exclusions, support, refund window, and delivery method without advertising unshipped assets.
3. Verify the payment processor's product, price, amount, currency, quantity, and checkout link/object against a stored approved configuration. Never substitute a similar object.
4. Before testing, define delivery-link expiry, requester verification, support-response target, refund window, dispute behavior, and currency for this business. Use sandbox/test mode to verify successful payment, failed payment, duplicate/replayed event, one initial delivery, expiry, authenticated renewal, refund preview/execution/readback, and dispute stop behavior.
5. Confirm support can read, reply, preserve threading, and escalate. Do not expose another buyer's information.
6. Confirm privacy and terms describe the services and data actually used. Do not add third-party trackers.
7. Define first-party source tags and test that only allowed values reach aggregate measurement.
8. Complete the launch-readiness checklist and save evidence references, never secrets or customer data.
9. Keep live checkout disabled throughout Play 6. This play never authorizes activation; the independently reviewed buyer-path plan is an input to Play 7, where the launch plan and dated/frozen prelaunch rules must also pass before the owner may approve activation.
10. Save `work/06-buyer-path/BUYER-PATH-PLAN.md` and update `STATUS.md`.
11. Give the exact plan, QA-passed package hash, copied launch-readiness record, and test evidence to a reviewer who did not build the buyer path. The reviewer checks every advertised state, offer/package parity, configuration identity, replay/delivery/refund/support/privacy behavior, evidence gaps, activation/rollback, and fail-closed behavior.
12. Save the independent result as `work/06-buyer-path/BUYER-PATH-QA-REPORT.md` with evidence and exactly one verdict: `PASS`, `REWRITE`, or `BLOCKED`. Any changed plan requires a new review.

## Produced artifact

`BUYER-PATH-PLAN.md` with:

- state diagram or table;
- exact offer/checkout/delivery identifiers stored privately;
- landing-copy requirements;
- sandbox acceptance evidence;
- support/refund/privacy behavior;
- first-party measurement tags;
- launch checklist result;
- activation and rollback steps;
- true owner/access blockers.

`BUYER-PATH-QA-REPORT.md` with reviewer independence, exact plan/package identity, test method, defects, evidence references, and one verdict.

## Success criteria

- Store copy and the QA-passed archive agree.
- Price, currency, quantity, product, price object, and checkout link/object agree.
- Paid, failed, replayed, delivery, expiry, renewal, refund, and dispute paths have deterministic outcomes.
- One paid order causes no more than one initial delivery.
- Delivery links expire according to the predeclared business policy and security risk review.
- Support and refund claims match actual capability.
- Checkout remains closed if any critical acceptance item is missing.
- The independent `BUYER-PATH-QA-REPORT.md` verdict is `PASS` for the exact plan and package hash.
- No activation occurred during Play 6; checkout remains disabled pending the verified Play 7 plan and dated/frozen prelaunch rules.

## Stop conditions

- A real payment is proposed without owner approval.
- Product/price/configuration mismatch exists.
- Delivery, support, refund, or privacy capability is missing or untested.
- The page claims an unshipped asset or guaranteed result.
- A dispute, security issue, credential exposure, or customer-data mismatch appears.
- No independent reviewer is available; keep the buyer-path gate `BLOCKED` rather than self-certifying it.

## Next play

Proceed to Play 7 only after the independent buyer-path verdict is `PASS`. Checkout activation remains prohibited during this play and becomes eligible for owner review only after Play 7 saves/verifies its launch plan, dates/freezes the prelaunch rules, checkpoints status, and passes every applicable gate.
