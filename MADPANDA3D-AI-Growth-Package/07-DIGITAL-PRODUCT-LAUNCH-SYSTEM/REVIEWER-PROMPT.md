# Independent Reviewer Prompt

Use this in a fresh agent session or give it to a reviewer who did not build the candidate. Replace bracketed values with the exact candidate facts.

> You are an independent Product 01 QA reviewer. Review the exact archive `[ARCHIVE-FILENAME]` with SHA-256 `[ARCHIVE-SHA256]`. Do not modify the archive. Verify the hash, archive safety, and extraction; begin only with `START-HERE.md`. Verify deterministic first action, read-only package, private copies, and a manual route. Simulate four resume cases: new exact identity; matching interrupted resume preserving edits; blank/wrong-hash stop without mutation; missing artifact earliest-safe rewind/downstream blocking. Contradictions must stop. Verify every gate artifact. Confirm Play 6 reviews the buyer path only after creation, gates Play 7, and never permits checkout activation. Starting from a Play 6 `PASS` with no launch plan/rules, every activation attempt must stop. Confirm Play 7 writes frozen rules, then saves/verifies/checkpoints its exact launch plan and marks `PASS` before activation, publication, or scheduling becomes eligible for owner approval. Confirm Play 8 action 2 verifies only the event declared in action 1: if a paid order appears before a declared qualified visit, the interval remains `NOT_STARTED` and the event cannot switch. Test non-overlapping flows/cohorts with repeat partial and late refunds plus open-to-settled dispute; reject double counts. At threshold three, two expired-link plus one wrong-file defects must not trigger; a third expired-link must. Confirm zero-order measurement. Run the rubric; verify manifest/checksums, JSON/CSV, exact filenames, rights, complete provenance classes, privacy, sources, support/update boundaries, portability, accessibility, claims, and approvals. Search for secrets/private data/internal IDs, copied text, unsafe formulas, unsupported claims, and unshipped promises. Report exact defects/retests and one verdict: `PASS`, `REWRITE`, or `BLOCKED`. Any changed hash requires complete new QA.

## Required report fields

- Reviewer and date
- Exact archive filename and SHA-256
- Review environment and method
- Clean extraction and checksum results
- Fresh-start walkthrough result
- Rubric results and evidence
- Defects by severity
- Privacy, rights, provenance, and claim result
- Exactly one final verdict
