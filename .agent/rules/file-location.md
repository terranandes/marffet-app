---
trigger: always_on
---

# File System Authority & Ownership Protocols

## 1. Governance Principles
- **Exclusivity:** Agents must strictly adhere to write permissions. Do not modify files owned by other agents unless explicitly instructed by `[PL]`.
- **Root Directory:** All product-related documentation resides in `./docs/product/` or the root `./`.
- **Traceability:** All generated files must reflect the authoring agent's identity in the content or metadata.

---

## 2. Product Vision & Public Interface
**Owner:** `[PM]` (Product Manager)

| File Path | Target Audience | Purpose |
| :--- | :--- | :--- |
| `./README.md` | **Developers / Repo Watchers** | Technical entry point. Explains how to build, contribute, and install. (GitHub landing page). |
| `./product/README.md` | **End-Users** | User Manual. Explains how to *use* the App. No technical jargon. |
| `./product/datasheet.md` | **Stakeholders / Business** | Product specs, market fit, and feature summary. |
| `./product/social_media_promo.md` | **Customers / Promotion** | Social media promo |

---

## 3. Technical Specifications & Architecture
**Owner:** `[SPEC]` (AntiGravity) or `[OSPEC]` (Opencode CLI)

> **Directive:** These files form the "Law" of the project. `[CODE]` and `[UI]` must strictly follow these.

- `./docs/product/specification.md` (Master Logic Document)
- `./docs/product/backup_restore.md`
- `./docs/product/crawler_architecture.md`
- `./docs/product/data_pipeline.md`
- `./docs/product/auth_db_architecture.md`

---

## 4. Project Management & Orchestration
**Owner:** `[PL]` (Project Leader)

### Task Tracking
- `./docs/product/tasks.md`
    - **Rule:** Must be updated dynamically. `[PL]` ensures this reflects the live status of all agents.

### Meeting Records
- `./docs/meeting/meeting_notes_YYYY_MM_DD_v{version}.md`
    - **Format:** Strict ISO date format.
    - **Trigger:** Auto-generated after any multi-agent synchronization session.

### Technical Stack (Shared Ownership)
- `./docs/product/software_stack.md`
    - **Primary Owner:** `[PL]` (Maintains structure)
    - **Contributors:** `[CODE]`, `[UI]` (Provide library details)

---

## 5. Quality Assurance & Verification (Strict Separation)
**Warning:** `[CV]` and `[GCV]` possess distinct memory and logic streams. **Cross-contamination is prohibited.**

### Standard Verification (AntiGravity)
**Owner:** `[CV]`
**Access:** `[GCV]` is **FORBIDDEN** from modifying these files.
- `./docs/product/test_plan.md` (Master Test Strategy)
- `./tests/unit/*` (Unit Tests)
- `./tests/e2e/*` (e2e_suite.py & UI Tests)
- `./tests/integration/*` (Verification scripts)
- `./tests/debug_tools/*` (debug_*.py, inspect_*.py, probe_*.py)
- `./tests/ops_scripts/*` (Admin/Ops scripts)

### Gemini Advanced Verification (Gemini CLI)
**Owner:** `[GCV]`
**Access:** `[CV]` is **FORBIDDEN** from modifying these files.
- `./docs/product/test_plan_gemini.md` (Complex reasoning test plans)
- `./tests_gemini/*` (Tests requiring multimodal or advanced reasoning)

---

## 6. Issue Tracking (Jira Simulation)
**Shared Owners:** `[CV]` & `[GCV]`

> **Directive:** When filing a ticket, the filename must explicitly identify the reporter.

- **Path:** `./jira/*`
- **Naming Convention:** `{ISSUE_TYPE}-{SERIAL_ID}-{REPORTER_AGENT_ID}_{BUG_BRIEF_DESCRIPTION}.md`
    - Example: `BUG-110-GCV_mobile_google_login.md`
    - {SERIAL_ID} must be Decimally-Incremetal
- **Content Requirement:** The file content must strictly state *which agent* discovered the bug.