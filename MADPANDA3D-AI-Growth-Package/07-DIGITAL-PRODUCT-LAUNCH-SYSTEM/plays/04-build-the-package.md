# Play 4 — Build the Package

## Objective

Turn the approved product brief into a complete, versioned, portable customer package.

## Required inputs

- Frozen `PRODUCT-BRIEF.md`
- Approved owned source material
- Package folder and version identifier

## Tool capability needed

- **Needed:** file creation and storage
- **Helpful:** document conversion, archive creation, checksums, link checking
- **Manual fallback:** create and review each file locally, then compress the folder with the operating system

## Ordered actions

1. Create a clean build folder named with product slug and semantic version.
2. Copy only approved source material into a separate curation area. Never build directly from private originals.
3. Rewrite source knowledge for the named buyer, removing internal paths, account identifiers, client facts, credentials, private prompts, and vendor assumptions that do not generalize.
4. Build the start file first. Make the first action obvious and require minimal reading.
5. Build each workflow with objective, inputs, capabilities, manual fallback, ordered actions, produced artifact, success criteria, stop conditions, and next step.
6. Build templates and scorecards with headers, definitions, and one clearly labeled fictional example only if needed.
7. Check links, headings, filenames, encoding, formulas, and portability. Avoid macros and executable content.
8. Create `MANIFEST.json` with package identity, version, file jobs, inventory, use-rights summary, and hashes for every customer-content file except `MANIFEST.json` and `SHA256SUMS.txt`.
9. Create `SHA256SUMS.txt` after the manifest; hash every package file except `SHA256SUMS.txt`, including `MANIFEST.json`. This avoids a circular self-hash while allowing the manifest and customer content to be verified.
10. Create a ZIP from the package root. List the archive and test extraction into a new temporary folder.
11. Save a build record with source version, build time, file count, archive hash, and known limitations.
12. Update `STATUS.md`.

## Produced artifact

- Versioned customer package folder
- Versioned ZIP archive
- `MANIFEST.json`
- `SHA256SUMS.txt`
- `work/04-build/BUILD-RECORD.md`

## Success criteria

- Every promised file exists, opens, and has a distinct job.
- The start command works from a fresh agent conversation.
- Every play includes all required sections and a manual fallback.
- No forbidden data, internal identifiers, secrets, private client material, copied competitor material, or broken links are present.
- The manifest and actual file inventory agree.
- Hash verification passes.
- Archive listing and clean extraction pass.
- The exact built version is not yet advertised as shipped unless its release path confirms publication.

## Stop conditions

- A promised asset cannot be completed.
- Source provenance or redistribution rights become uncertain.
- The clean-package scan finds sensitive or internal-only data.
- Archive or hash verification fails after correction attempts.

## Next play

Freeze the built archive and hand it to an independent reviewer for Play 5. Do not silently edit the reviewed archive; any edit creates a new candidate and requires re-QA.
