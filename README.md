# CCAR-F Study Studio

A browser-based spaced repetition and quiz app for Claude Certified Architect — Foundations.

## Run locally

Run from the repository root (the directory containing `dist/`). In the original workspace this is `ccar-study/`.

```bash
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:4173. No API key, account, package install, or build step is needed. Serve through HTTP rather than opening `index.html` directly because the app uses JavaScript modules.

## Daily study and community packs

Open **Community packs** to check or uncheck optional banks. Changes apply to flashcards, quizzes, mocks, library, and Anki exports. Disabled content keeps its schedules, bookmarks, and quiz history. Original questions are always enabled. A quiz already in progress remains resumable even if its pack is disabled.

For personal Anki decks, choose **Import Anki deck**, select an `.apkg`, `.txt`, or `.tsv` file, inspect the fields, and add it. In **Flashcards**, use the deck selector to review that deck directly. Basic text and cloze notes are supported, including modern Zstandard-compressed APKG collections. Media, custom Anki templates, automatically generated reversed cards, and Anki scheduling are not imported. Personal decks are flashcards only and are not considered reviewed CCAR-F question content. Limits: 25 MB per file, 10,000 personal cards across up to 50 decks, and 3 MB serialized state for new imports. Image/audio-only notes are skipped.

Imports and history remain in browser localStorage. No account, analytics, file upload, or external CDN is used. Pack preferences, daily activity, review schedules, quiz history, and personal decks survive reloads. **Settings → Export progress JSON** backs up all of them; restore transfers them to another browser. Different addresses have separate storage: export from localhost or the earlier hosted site, then restore on GitHub Pages. Clearing browser data removes local progress. Private browsing may discard it when closed.

## GitHub Pages

The workflow in `.github/workflows/pages.yml` tests the app and publishes only `dist/` after a push to `main`. In repository **Settings → Pages → Build and deployment**, choose **GitHub Actions**. The published URL appears in the workflow deployment. All asset URLs are relative, so project Pages URLs work without a build or base-path setting. Personal decks and progress are never part of the Pages artifact.

## Included

- 79 original questions by default; opt into 255 additional licensed community questions (334 total) covering all 30 objectives in five domains.
- Configurable practice quizzes, domain drills, source-bank filters, mistakes and saved-item filters; paginated searchable library.
- 60-item, 120-minute mock exams with rounded domain allocations of 16 / 11 / 12 / 12 / 9.
- Shuffled answer positions; single and multiple-response questions; exact-set scoring.
- Source links, explanations, question library, bookmarks, and searchable objectives.
- SM-2-inspired scheduling, daily new/review limits, streaks, coverage, accuracy, and session history.
- Saved active quiz sessions. Mock deadlines continue while the app is closed.
- Validated JSON backups and Anki-compatible TSV export.
- Responsive desktop/mobile layout and keyboard flashcard controls: Space to reveal, 1–4 to rate.

Progress uses browser localStorage. There is no cross-device account sync. Export a backup to transfer progress; restore replaces the destination browser’s progress. Flashcard browsing does not change scheduling; quiz attempts do not alter recall intervals.

## Content policy

Question answers are grounded in official Anthropic documentation and the Anthropic-authored exam guide. The expanded bank adapts licensed community practice material: 88 items from Alexio Cassani and contributors (CC BY-SA 4.0), 111 from Haytam Aroui (MIT), and 56 from choychoy1 (CC BY 4.0). Each adapted item includes official references and author/license credits; credits also accompany Anki exports. See NOTICE.md, dist/licenses/, and research/bank-audit.json for provenance, pinned revisions, changes, and nine excluded candidates. Adaptations retain their origin licenses.

Cookbook recipes and Anki decks remain supplementary resources. Unlicensed decks were not imported. Current documentation takes precedence over obsolete terminology. Reviewed 2026-10-08; this is a content review, not psychometric calibration. Rebuild the imported bank offline with `python3 scripts/build-bank.py`; the normalized source snapshot is research/upstreams/raw.json.

This is an independent study aid, not an endorsed exam product. Practice percentages are not Anthropic scaled scores. The mock follows domain weights and duration; it does not reproduce official exam forms or the four-of-six scenario selection mechanism.

## Scheduling

Again schedules a 1-minute relearning step and resets successful repetitions. Hard schedules a 10-minute step for a new/relearning card, or 1.2 times the current day interval for an established card. Good schedules 1 day, then 6 days, then interval multiplied by ease. Easy begins at 4 days and expands established intervals. Ease is bounded between 1.3 and 3; intervals are capped at 36,500 days. The scheduler is SM-2-inspired, not Anki FSRS. Session queues are snapshots; an Again card is available again after its due time in a new session. Daily review limits apply to existing cards; new cards have a separate limit.

## Verification

With Node.js installed:

```bash
node tests/core.test.js
```

Fourteen tests check pack opt-in and history retention, personal-deck validation, text import parsing, expanded-bank provenance and exclusions, preservation of original IDs, unique IDs and task coverage, weighted mock sampling, recall intervals and limits, multiple-response scoring, daily queues, date-based streaks, and backup validation.

Files: `dist/content.js` is the source-linked bank; `dist/core.js` contains scheduling and validation; `dist/app.js` contains the interface; `dist/styles.css` contains responsive styles. This is a static website and can be served by any static HTTP host.

## Contributing a community pack

See [CONTRIBUTING.md](CONTRIBUTING.md). Public packs must have redistribution permission and preserve attribution. Personal imports do not automatically become public packs. See [LICENSE-CONTENT.md](LICENSE-CONTENT.md) for the separation between MIT app code and third-party question licenses.
