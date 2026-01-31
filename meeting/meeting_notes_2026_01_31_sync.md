# Meeting Notes: Next.js Migration & Sync
**Date:** 2026-01-31
**Attendees:** [PL], [PM], [SPEC], [CODE], [UI], [CV]

## 1. Project Progress
- **Next.js Migration:** **COMPLETED.** Legacy UI (`app/static`) is gone. Backend is pure API.
- **Race Stability:** **RESOLVED.** "Trend Architecture" deployed. No more OOM/Hang ups.
- **UX Enhancement:** Race now supports **Quarterly** frames + **Playback Slider**.

## 2. Current Status (Local vs Remote)
- **Local:** Pure Next.js. Legacy files deleted.
- **Remote (Zeabur):** Still has legacy until we push `master`.
- **Action:** [PL] waiting for user final "Commit & Push" command.

## 3. Discrepancies / Bugs
- **Bond ETFs:** Crawler logs "Delisted" for some Bond ETFs (`00937B.TW`).
    - *Mitigation:* [CODE] added `.TWO` suffix logic. It works in UI, logs are just noise from cached attempts.
- **Legacy Routes:** [CV] confirmed `app/main.py` is clean.

## 4. Feature Roadmap (Next Phase)
- **Immediate:**
    - Commit Migration.
    - Full Deploy.
- **Deferred:**
    - "Dynamic Stock Naming" (Crawler update).
    - "MoneyCome Tab" (New feature).

## 5. Mobile Web Layout
- **[UI] Report:** Next.js sidebar uses relative paths. Mobile menu works.
- **[PM] Feedback:** The "My Race" slider needs to be tested on touch screens (Draggable?).
    - *Response:* Standard `<input type="range">` is touch-friendly by default.

## 6. Action Items
1.  **[PL]** Execute `git add .` and `git commit` to finalize removal.
2.  **[CODE]** Monitor "Bond ETF" logs in next crawler run.
3.  **[BOSS]** Approve deployment to Zeabur.

**Meeting Adjourned.**
