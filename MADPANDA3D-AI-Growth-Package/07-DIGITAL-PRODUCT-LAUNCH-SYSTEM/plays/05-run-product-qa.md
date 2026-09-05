# Play 5 — Run Product QA

## Objective

Have a reviewer who did not build the candidate determine whether it is useful, complete, safe, accurate, and ready for the buyer-path test.

## Required inputs

- Frozen candidate archive and archive hash
- `PRODUCT-BRIEF.md`
- A private working copy of `assets/product-qa-rubric.md`
- `REVIEWER-PROMPT.md`
- Clean temporary review folder

## Tool capability needed

- **Needed:** file reading, archive extraction, and document creation
- **Helpful:** link checker, JSON/CSV parser, checksum tool, second independent agent
- **Manual fallback:** a second person extracts the archive and follows the rubric without builder guidance

## Ordered actions

1. Record the candidate filename and SHA-256 hash before review.
2. Extract it into an empty folder. Fail if extraction writes outside that folder or contains unexpected executable files.
3. Review as the named buyer, starting only with `START-HERE.md`.
4. Use `REVIEWER-PROMPT.md` to test the activation command in a fresh agent session when possible. Record where the agent asks, assumes, stalls, or performs too much at once.
5. Verify every promised outcome against the package and manifest.
6. Parse JSON and CSV files. Check Markdown links and required play sections.
7. Search for credentials, customer data, internal paths, account IDs, private client material, unsupported claims, copied wording, and instructions that permit unconfirmed external actions.
8. Score the rubric and classify defects as critical, major, or minor.
9. Issue exactly one verdict: `PASS`, `REWRITE`, or `BLOCKED`.
10. If rewritten, create a new candidate hash and re-run every affected check plus the package-level checks.
11. Save `work/05-qa/PRODUCT-QA-REPORT.md` and update `STATUS.md`.

## Produced artifact

`PRODUCT-QA-REPORT.md` with:

- reviewer and review date;
- candidate filename and hash;
- environment and method;
- rubric scores and evidence;
- defect list with severity, path, expected behavior, and retest;
- privacy/security scan result;
- activation walkthrough result;
- final verdict.

## Success criteria

- Reviewer independence is stated.
- All critical rubric rows pass; no critical defect remains.
- Package identity, version, contents, and claims agree.
- A new buyer can identify the first action without builder assistance.
- External actions remain human-approved and evidence-backed.
- The report references the exact candidate hash.

## Stop conditions

- Reviewer is given only selected files rather than the exact archive.
- Archive hash changes during review.
- Critical leakage, unsafe action authority, missing promised content, or unusable start flow is found.
- No independent reviewer is available; mark `BLOCKED`, not self-certified.

## Next play

Proceed to Play 6 only with a `PASS` verdict on the exact candidate archive.
