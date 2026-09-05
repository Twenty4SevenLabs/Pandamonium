# Play 3 — Design the Product

## Objective

Specify the smallest digital product that delivers the promised outcome and can be built, checked, supported, and updated.

## Required inputs

- Passed `OFFER-EVIDENCE-PACKET.md`
- Owned, redistributable source inventory
- Delivery format and buyer tool constraints

## Tool capability needed

- **Needed:** document creation and file storage
- **Helpful:** spreadsheet creation, diagram/media tools
- **Manual fallback:** write the product brief and manifest in a local editor

## Ordered actions

1. Convert the offer into one observable completion outcome.
2. Map the buyer journey from opening the package to completing the outcome. Remove steps that do not change the result.
3. Choose the format based on use: agent-readable Markdown/CSV/JSON for guided execution; human-readable PDF only when it improves use.
4. Define each file by job, required input, produced output, and acceptance check.
5. Include a start file, status/resume mechanism, workflow, templates, examples only when owned, a provenance record, a commercial-output-rights summary, and a manifest.
6. Define use rights, versioning, update policy, accessibility needs, privacy/safe-use rules, support boundary, and third-party dependencies.
7. Define what is not included: done-for-you work, guaranteed outcomes, credentials, paid tools, or unrelated future products unless genuinely part of the offer.
8. Set a fixed build scope and change-control rule: new ideas go to a backlog unless they fix a critical acceptance gap.
9. Write `work/03-design/PRODUCT-BRIEF.md` and update `STATUS.md`.

## Produced artifact

`PRODUCT-BRIEF.md` with:

- product name, version, buyer, problem, promise, price hypothesis, and format;
- buyer completion outcome;
- customer journey;
- exact package manifest and file purposes;
- source provenance and redistribution status;
- use rights and update policy;
- dependencies and manual fallbacks;
- exclusions, risks, and support boundary;
- file-level and package-level acceptance tests;
- deferred backlog.

## Success criteria

- A buyer can receive value without reading a long manual first.
- Every file has a distinct purpose tied to the promised outcome.
- The package has a resume/status mechanism.
- Source ownership and redistribution rights are documented.
- No credentials, customer data, private client work, internal identifiers, or unnecessary vendor-specific assumptions are included.
- Acceptance tests can determine pass or fail without relying on taste alone.
- The build scope is small enough to complete and support.

## Stop conditions

- Source rights are unresolved.
- The package depends on unavailable paid tools with no manual fallback.
- The promised outcome cannot be tested.
- Scope continues expanding without evidence of necessity.

## Next play

Freeze the product brief and proceed to Play 4. Changes after freeze require a recorded reason and a re-run of affected QA checks.
