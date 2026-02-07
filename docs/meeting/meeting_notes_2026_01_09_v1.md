# Agents Sync-Up Meeting Notes
**Date:** 2026-01-09
**Version:** v1
**Participants:** [PM], [PL], [SPEC], [CODE], [UI], [CV]

---

## 1. Project Progress & Achievements
**[PM]**: Excellent work everyone. We have successfully **Verified Phase 4: Social Features**. This was a critical milestone. We now have a Leaderboard and secure Public Profiles.
**[CV]**: Confirmed. `tests/test_social.py` is green. Logic for ROI calculation and Privacy sanitization is solid.
**[CODE]**: The backend is stable. We also deployed a critical fix for the **"Laggy Google Auth/Chat"** issue. I refactored `app/main.py` to run the blocking Google GenAI calls in a threadpool, which should unblock the event loop.
**[PL]**: We also addressed the **System Instability**. The "Reconnecting to remote authority" issue was likely caused by too many active MCP servers (Brave, Tavily, etc.) saturating the VS Code connection.
**[PL]**: I have **PAUSED** the "Side Quests" for tooling setup and reverted to a minimal MCP config (Memory + Smart Coding). This should stabilize the environment for Terran.

## 2. Bug Triage
*   **[Critical] Google Auth Latency**:
    *   *Status*: **Fix Deployed**.
    *   *Root Cause*: Synchronous API calls in Async endpoints (`chat_with_mars`).
    *   *Fix*: Implemented `run_in_threadpool`.
*   **[Critical] System Lag/Disconnects**:
    *   *Status*: ** mitigated** (Paused heavy MCPs).
    *   *Root Cause*: Resource exhaustion from multiple external MCP servers.
    *   *Action*: Reverted to minimal config.

## 3. Features Implemented (Phase 4)
*   User Leaderboard (Rank by ROI/Wealth).
*   Public Profile Modal (Read-Only, Privacy-Sanitized).
*   Wealth Simulation Engine Upgrade (Share Accumulation).
*   Dynamic Start Year for Simulation.

## 4. Features Unimplemented / Deferred
*   **[UI]** "Wow" Factor: The UI is functional but could use more polish (animations, glassmorphism) to meet the "Premium" requirement.
*   **[DevOps]** Production Deployment: We are still running locally.

## 5. Planning: Phase 5 & Next Steps
**[PM]**: We are at a fork. We can either:
1.  **Deploy**: Move to a real server (AWS/GCP/Vercel).
2.  **Automate**: Start Phase 5 (Automated Trading / Rebalancing).
3.  **Polish**: Spend a cycle purely on UI/UX "Wow" factor.

**[SPEC]**: If we go for Automation (Phase 5), I need to draft the specs for the "Trading Engine" and "Safety Guardrails".
**[UI]**: If we go for Polish, I want to redesign the Public Profile to look like a "Card" or "NFT" that serves as a badge of honor.

## 6. Deployment Completeness
**[CODE]**: `start_app.sh` is reliable. Dependencies are locked.
**[CV]**: Tests are passing.
**[PL]**: Environment is currently "Local Only".

---

## [PL] Summary for Terran
*   **Phase 4 Verified**: Social features are done.
*   **Stability Fixed**: Lag should be gone (Code fix + MCP reduction).
*   **Ready to Run**: Use `./start_app.sh`.
*   **Decision Needed**: User to decide next focus (Deployment vs. Auto-Trading vs. UI Polish).
