# Agents Sync-Up Meeting: 2026-01-07

**Date**: 2026-01-07
**Attendees**: [PM], [PL], [SPEC], [UI], [CV], [CODE]
**Topic**: Post-MCP Installation Check & Phase 4 (Social) Status

---

## 1. Project Progress & Side Quests ([PL])
**[PL]**: Great work team. The "Side Quest" to install and configure MCP servers is fully complete.
- **Sentry**: Installed & Configured (Python).
- **Sequential Thinking**: Installed (Node/Npx).
- **Brave Search**: Installed (Node/Npx) & Fixed (Node v22 path).
- **Smart Coding**: Installed (Node/Npx) & Fixed.
- **Node.js**: Upgraded local environment references to v22.21.1 to solve legacy syntax errors.

We are now compliant with the "Smart MCP" rules.

## 2. Phase 4: Social Features Status ([PM] & [CODE])
**[PM]**: We marked "Social Features Implementation" as done in `task.md`. We have a Leaderboard and Public Profiles. But I need to know: is this *production ready*?
**[CODE]**: The backend logic is solid.
- `GET /api/leaderboard`: Returns top users by ROI.
- `GET /api/portfolio/public/{id}`: Returns sanitized portfolio data.
- Database: `users` table has cached stats (`total_wealth`, `total_roi`) to speed up the leaderboard.

**[UI]**: Frontend is implemented.
- Leaderboard table displays Rank, Avatar, Nickname, ROI.
- Clicking a user opens the Read-Only Portfolio Modal.
- Asset Allocation charts are live for public profiles.

## 3. Verification & Safety ([CV] & [SPEC])
**[CV]**: The code is there, but I haven't run a full regression or targeted test suite for Social yet.
- Need to verify `tests/test_social.py` (if it exists) or create it.
- Need to run a browser flow to ensure the Public Link actually opens for a non-logged-in user (incognito mode test).

**[SPEC]**: **Critical Warning**: Public profiles must strictlY adhere to the Data Privacy Spec.
- **No PII**: No email, no Google ID, no session tokens in the public JSON response.
- **Sanitized**: Only stock tickers, weights, and calculated percentages.

## 4. Next Steps ([PL])
**[PL]**: Okay, the path forward is clear.
1.  **Verify Phase 4**: [CV] to run verification.
2.  **Privacy Audit**: [SPEC] to review the `/api/portfolio/public/{id}` payload.
3.  **Documentation**: Update `software_stack.md` if we added new libs (we didn't, mostly logic).

**Action Items**:
- [CV] Run verification for Social Features.
- [CODE] Ensure the app is running for Terran to check.

---

## How to Run the App (for Terran)

1.  **Backend**:
    ```bash
    cd ~/github/martian
    source .venv/bin/activate
    python app/main.py
    ```
2.  **Frontend**: (Served statically by Backend at `http://localhost:8000`)
3.  **Access**: Open `http://localhost:8000` via the browser tool or your local browser.

**Report to Terran**:
[PL]: "Boss, MCPs are solid. Phase 4 code is done but needs 'The Critic' [CV] to verify privacy and logic. We are ready to run the app and verify."
