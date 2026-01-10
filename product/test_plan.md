# Test Plan & Automation Strategy

## 1. Testing Levels

### 1.1 Backend API Verification (Headless)
-   **Tool**: `verify_api_headless.py` (Python `requests` script).
-   **Scope**:
    -   Server Availability (Port 8000).
    -   Core Endpoints: `/`, `/api/leaderboard`, `/api/public/profile/{id}`.
-   **When to Run**: Pre-commit, Post-deployment.

### 1.3 Data Integrity Verification (Automated)
-   **Tool**: `verify_targets.py`
-   **Scope**:
    -   Validates numeric correlation between Simulation Logic and Golden Excel (`stock_list_s2006e2025_filtered.xlsx`).
    -   Checks data availability for all 1800+ targets (TWSE, TPEx, Bond ETFs).
-   **When to Run**: Weekly or after major crawler updates.

### 1.4 Frontend UI Automation (Planned)
-   **Tool**: Playwright (via `mcp-playwright`).
-   **Scope**:
    -   User Login Flow (**Pre-requisite**: Must execute on host with valid Google Auth Redirect URI).
    -   "Mars Strategy" Tab: Verify simulation chart renders.

## 2. Manual Verification Checklist
1.  **Load App**: Check for console errors in DevTools.
2.  **Simulation**: Change "Start Year" -> Verify chart updates.
3.  **Profile**: Click user on Leaderboard -> Verify Modal appears with correct info.
4.  **AI Bot**: Open Chat -> Ask "What is CAGR?" -> Verify intelligent response.

## 3. Bug Triage Process
-   **Severity 1 (Critical)**: App crash, Data leak. -> Immediate Fix.
-   **Severity 2 (Major)**: Feature broken (e.g., Chart not loading). -> Fix in current sprint.
-   **Severity 3 (Minor)**: UI glitch, typo. -> Backlog.
