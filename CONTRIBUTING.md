# Contributing content packs

Users enable existing community banks with checkboxes on Community packs. For their own Anki material, the local import flow requires no repository changes. Importing does not publish the file.

To add a reviewed public question bank:

1. Verify an explicit license permits redistribution and adaptation. Public availability alone is insufficient. Do not add live or recalled exam questions, paid exam dumps, unlicensed APKG decks, or copied Anthropic documentation.
2. Record upstream author, URL, license, pinned revision, and adaptations in `scripts/build-bank.py`. Preserve the full notice in `dist/licenses/<origin>.txt` and credit the pack in NOTICE.md.
3. Add normalized upstream records to `research/upstreams/raw.json`, with a distinct origin and stable IDs. Map each question to the official exam objectives and official documentation. Review answer keys, ambiguity, and current product behavior; record exclusions and corrections in the builder.
4. Run `python3 scripts/build-bank.py`. It emits `dist/imported-bank.js` and the audit. The app derives pack checkboxes from bankOrigins automatically; no UI change is needed. New packs are disabled until the user opts in.
5. Update expected bank counts in tests, run `node tests/core.test.js`, and verify pack toggles, shuffled answers, per-item credits, and exports in a browser.

Keep existing IDs stable. Updates retain local user schedules and quiz history by ID. Pack disabling pauses content without deleting history. Adapted CC BY-SA content must retain CC BY-SA 4.0; do not relabel all content as MIT.

# Development

This app has no install/build step. Serve `dist/` with Python or another static server. APKG parsing uses pinned, vendored browser parsers in web workers. The vendor manifest records download URLs and SHA-256 hashes; preserve dependency license files. Imported note HTML is reduced to plain text and rendered escaped. Do not execute Anki templates or add uploads of user decks.
