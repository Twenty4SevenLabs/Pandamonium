# Play 8 — Run the 30-Day Evidence Loop

## Objective

Use real aggregate traffic, order, fulfillment, support, and feedback evidence to improve distribution or the offer without moving the rules after seeing results.

## Required inputs

- For action 1: proposed start event, 30-day interval, time zone, thresholds, and decision hypotheses
- For actions 2–10: dated/frozen `work/08-scorecard/PRELAUNCH-DECISION-RULES.md`
- Private working copies of `revenue-and-feedback-scorecard.csv` and `delivery-defect-log.csv`
- Aggregate storefront, checkout, order, refund, dispute, delivery, support, and channel data
- Change log and current released package hash

## Tool capability needed

- **Needed:** spreadsheet/document creation and aggregate metric access
- **Helpful:** storefront analytics, payment reporting, support-age reporting, and channel analytics
- **Manual fallback:** update the copied scorecard from provider dashboards using aggregate totals; never copy raw customer records or private message bodies into it

## Ordered actions

1. Complete this action during Play 7 before any activation or publication: write, date, and freeze `PRELAUNCH-DECISION-RULES.md`. Declare the start event, time zone, qualified-visit definition, minimum qualified visits, minimum paid orders or other completion signal, maximum refund rate, support-response target, the integer recurrence threshold for one fulfillment-defect class, and exact `PASS`, `REVISE DISTRIBUTION`, `REVISE OFFER`, and `STOP` decisions. Do not start the interval during this rule-design action.
2. Verify only the start event already declared and frozen in action 1; do not choose, replace, or reinterpret it after observing activity. Record the authoritative evidence reference and UTC timestamp, then start the interval. A declared qualified-visit event supports the zero-order/pre-sale path; a declared first-paid-order event supports a commerce path. If another event occurs first—for example, a paid order before a declared qualified visit—the interval remains `NOT_STARTED` until the declared event is verified. Any future event change requires a separately versioned test with new rules; it cannot retroactively start or alter this interval.
3. Use two row types in the scorecard. `PERIOD_FLOW` rows cover non-overlapping intervals and record visits, handoffs, newly paid unique orders, cash gross, fees, refund cash movements, settled dispute losses, net, support-over-target, and end-of-period open-dispute snapshots. `COHORT_SNAPSHOT` rows record one named order cohort as of a date: cohort window, unique paid orders, unique orders with any refund to date, and refund rate. Keep order/session identifiers only in a private deduplicating ledger; never put them in the aggregate scorecard.
4. Apply deterministic aggregation. Count an order once in `new_unique_paid_orders_flow` at its first successful payment. A late refund records its cash amount in the period when the refund occurs and updates the affected cohort's next snapshot; do not rewrite prior period flows. A partially or fully refunded order counts once in `cohort_unique_refunded_orders_snapshot`, even if refunded in multiple periods. `cohort_refund_rate_snapshot = cohort_unique_refunded_orders_snapshot / cohort_unique_paid_orders_snapshot`; if the denominator is zero, use `NOT_APPLICABLE`. `net_amount_flow = gross_amount_flow - payment_processor_fees_flow - refund_amount_flow - settled_dispute_loss_amount_flow`.
5. Treat `open_dispute_count_snapshot` and `open_dispute_amount_snapshot` as end-of-period snapshots; never sum them across rows. When an open dispute settles as a loss, remove it from the next open snapshot and count its loss exactly once in `settled_dispute_loss_amount_flow` for the settlement period.
6. Record each delivery defect in `work/08-scorecard/delivery-defect-log.csv` using one stable predeclared `defect_class`. Evaluate recurrence by counting only the same class inside the predeclared scope. Mixed classes never combine to meet the threshold.
7. Diagnose the narrowest bottleneck: reach, message, checkout, delivery, activation, or support.
8. Make no more than one reversible evidence-backed product or process change per review cycle. Record hypothesis, evidence, owner, expected signal, rollback, and result. Preserve prior buyers' eligible update access; version product changes and rerun affected QA.
9. Continue useful organic distribution without exceeding the owner's channel limits or repeating the same post.
10. At day 30, apply the frozen rules exactly, then save `work/08-scorecard/30-DAY-DECISION.md` and update `STATUS.md`. Do not move a threshold, redefine a visit, sum snapshots, or change cohort rules after seeing results.

## Produced artifact

- `work/08-scorecard/PRELAUNCH-DECISION-RULES.md`
- `work/08-scorecard/revenue-and-feedback-scorecard.csv`
- `work/08-scorecard/delivery-defect-log.csv`
- `work/08-scorecard/30-DAY-DECISION.md` with metrics, evidence, change history, gate result, and next action

## Success criteria

- Rules are dated and frozen before launch.
- Period flows are non-overlapping; cohort and open-dispute snapshots are labeled and never summed.
- Unique paid/refunded order counts, late refunds, partial refunds, settled/open disputes, gross, fees, refunds, and net reconcile or differences are explained.
- Delivery recurrence counts only one stable defect class inside the frozen scope.
- Zero-order periods still record qualified visits, checkout handoffs, objections/feedback, delivery/support readiness, and the declared distribution/offer decision; order-dependent rates are `NOT_APPLICABLE`.
- Customer identities and private message bodies are excluded.
- Product and distribution changes are versioned, bounded, and attributable to evidence.
- Refund rate, fulfillment defects, and support age are considered alongside sales.
- The end decision follows the predefined rules.

## Decision-rule design

- If reach is below the declared visit floor, improve distribution before rebuilding the product.
- If reach is sufficient but the declared completion outcome misses, revise the offer once and version/retest affected materials.
- If operational safety, delivery, support, refund, or dispute limits fail, fix or stop the operation before expanding it.
- Thresholds are business hypotheses, not universal benchmarks or guarantees. The fictional walkthrough shows one example only.

## Stop conditions

- A dispute, suspected fraud, security incident, credential exposure, recurring fulfillment defect, or material data mismatch appears.
- Metrics cannot be reconciled.
- A proposed change breaks existing buyer access or makes an unsupported claim.
- The owner proposes moving the rules after seeing poor results.

## Next play

If the predeclared `PASS` rule is met, document the operating baseline and continue responsibly. Otherwise take only the predeclared revise-or-stop action and begin a new, explicitly defined test period after versioning affected materials.
