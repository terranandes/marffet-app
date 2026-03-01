# Zeabur DuckDB Remote Verification Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Conduct a strict, side-by-side verification of the Martian Investment System (UI, Data, features, and settings) comparing the local DuckDB environment against the newly deployed Zeabur remote DuckDB persistent volume.

**Architecture:** The verification will be executed in a dedicated local workspace while targeting the remote `martian-app.zeabur.app` and `martian-api.zeabur.app` URLs. We will use Playwright E2E automation for visual parity checking and direct API Python scripting for data correlation validation.

**Tech Stack:** Playwright (Python), FastAPI (`requests`), Next.js (Visual Inspection), DuckDB (Data Parity).

---

### Task 1: Environment & Auth Verification

**Scope:**
- Local UI (`localhost:3000`) vs Remote UI (`martian-app.zeabur.app`)
- Local API (`localhost:8000`) vs Remote API (`martian-api.zeabur.app`)

**Step 1: Verify System Health & Cold Starts**
- Check memory consumption during Zeabur container wake-up (is it adhering to `256MB` PRAGMA limit?).
- Verify HTTP 200 on `/health`.

**Step 2: Verify Auth Parity**
- Ensure "Continue as Guest" establishes a local session visually matching remote.
- Ensure Google Login routing properly handles the Cross-Domain callback on Zeabur (`.zeabur.app` domain sharing).

### Task 2: Core Tabs Data Parity (DuckDB Checks)

**Scope:**
- The overarching goal is ensuring the persistent Parquet-rehydrated volume on Zeabur serves identical calculation results to a fresh local DuckDB build.

**Step 1: Mars Strategy Verification**
- Input: `Universe` filter, `Duration > 3`, `Current Year Only`.
- Goal: Verify Zeabur returns ~1,066 stocks and math is identical to local.
- Specific Check: Ensure TSMC CAGR evaluates to exactly 19.41% remotely.

**Step 2: Trend & My Race Verification**
- Goal: Ensure the heavy ECharts rendering handles the remote latency without "Socket Hang Up" errors.
- Action: Load 5 heavy stocks simultaneously (e.g., TSMC, MediaTek). 

**Step 3: Bar Chart Race (BCR) & Compound Interest**
- Goal: Verify frontend data parsing from the backend JSON array correctly handles the sanitized NumPy objects on Zeabur.
- Action: Visual check of timeline animations.

**Step 4: Cash Ladder & Portfolio Views**
- Goal: Verify mobile responsiveness and deferred BUG-010-CV context constraints.
- Action: Compare desktop wide view vs mobile viewport behavior on Zeabur.

### Task 3: Feature-to-Feature Verification

**Step 1: Stock Search & Selection**
- Verify the dynamic ISIN name fallback strategy triggers successfully on the remote server for exotic ETFs.

**Step 2: AI Copilot Context Integration**
- Verify the internal Copilot prompt context successfully accesses the remote backend endpoints.

**Step 3: Data Export**
- Trigger the "Export Excel" function on the remote Mars Strategy. Verify `.xlsx` payload is constructed without timeout.

### Task 4: Setting Modal & Configuration

**Step 1: Verify User Settings Parity**
- Open modal, toggle Dark/Light themes.
- Manipulate default landing page targets (e.g., set default to Compound Interest) and verify local storage syncs correctly on next load from Zeabur frontend.

**Step 2: AI Copilot Server Key Fallback**
- Execute an AI Copilot request *without* providing a local API key in the UI settings.
- Goal: Verify the Zeabur backend intercepts and successfully utilizes the remote `.env` API key for inference.

---
### Execution Constraints (Guardian Rules)
- **Pacing:** All automated E2E tests targeting Zeabur must include a minimum 2-second sleep state between major tab transitions to monitor Zeabur memory thresholds (avoiding instant 502s).
- **Isolation:** Remote data generation MUST NOT pollute local `market.duckdb` states.
