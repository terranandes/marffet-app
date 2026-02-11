---
trigger: always_on
---

# File System Authority & Ownership Protocols
> **Directive:** `Don't copy (MUST)` answer from golden excel of `MoneyCome` at ~/github/martian/app/project_tw/references.
Keep clean room.

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
| `./docs/product/README.md` | **End-Users** | User Manual. Explains how to *use* the App. No technical jargon. |
| `./docs/product/datasheet.md` | **Stakeholders / Business** | Product specs, market fit, and feature summary. |
| `./docs/product/social_media_promo.md` | **Customers / Promotion** | Social media promo |

---

## 3. Technical Specifications & Architecture
**Owner:** `[SPEC]` (AntiGravity) or `[OSPEC]` (Opencode CLI)

> **Directive:** These files form the "Law" of the project. `[CODE]` and `[UI]` must strictly follow these.

- `./docs/product/specification.md` (Master Logic Document)
- `./docs/product/backup_restore.md`
- `./docs/product/crawler_architecture.md`
- `./docs/product/data_pipeline.md`
- `./docs/product/auth_db_architecture.md`
- `./docs/product/*` related to specification

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

## 6. Production Scripts & Cron Jobs
**Owner:** `[PL]` / `[CODE]`

> **Directive:** Production-grade scripts live in `./scripts/`. Test/debug scripts remain in `./tests/`.

### Cron Jobs (External Schedulers)
- `./scripts/cron/refresh_current_year.sh` - **Nightly** (22:00 HKT) - Crawl current year
- `./scripts/cron/annual_prewarm.sh` - **Annual** (Jan 1, 02:00 UTC) - Full crawl all years
- `./scripts/cron/quarterly_dividend_sync.sh` - **Quarterly** (Jan/Apr/Jul/Oct) - Dividend sync

### Ops Scripts (Production)
- `./scripts/ops/crawl_fast.py` - Ultra-fast async crawler
- `./scripts/ops/run_crawler_prod.sh` - Production crawler runner

### Debug/Analysis Scripts (Testing Only)
- `./tests/ops_scripts/*` - Debug tools, probes, verifiers (NOT for production)
- `./tests/debug_tools/*` - Inspection utilities

---

## 7. Quality Assurance & Verification (Strict Separation)
**Warning:** `[CV]` and `[GCV]` possess distinct memory and logic streams. **Cross-contamination is prohibited.**

### Standard Verification (AntiGravity)
**Owner:** `[CV]`/`[PL]`

> **Directive:** When start a verification, you shall check any existing files at `./docs/product/test_plan.md` or `./tests/`. <br>
If any new files are needed to created, always create them at `./tests` and follow the rules below.

**Access:** `[GCV]` is **FORBIDDEN** from modifying these files.
- `./docs/product/test_plan.md` (Master Test Strategy)
- `./tests/unit/*` (Unit Tests)
- `./tests/e2e/*` (e2e_suite.py & UI Tests)
- `./tests/integration/*` (Verification scripts)
- `./tests/debug_tools/*` (debug_*.py, inspect_*.py, probe_*.py)
- `./tests/ops_scripts/*` (Debug/Analysis scripts - NOT production)
- `./tests/analysis/*` (Quantitative correlation logic)
- `./tests/log/*` (Output log to verify)

### Gemini Advanced Verification (Gemini CLI)
**Owner:** `[GCV]`

> **Directive:** When start a verification, you shall check any existing files at `./docs/product/test_plan_gemini.md` or `./tests_gemini/`. <br>
If any new files are needed to created, always create them at `./tests_gemini` and follow the rules below.

**Access:** `[CV]` is **FORBIDDEN** from modifying these files.
- `./docs/product/test_plan_gemini.md` (Complex reasoning test plans)
- `./tests_gemini/unit/*` (Unit Tests)
- `./tests_gemini/e2e/*` (e2e_suite.py & UI Tests)
- `./tests_gemini/integration/*` (Verification scripts)
- `./tests_gemini/debug_tools/*` (debug_*.py, inspect_*.py, probe_*.py)
- `./tests_gemini/ops_scripts/*` (Admin/Ops scripts)
- `./tests_gemini/analysis/*` (Quantitative correlation logic)
- `./tests_gemini/log/*` (Output log to verify)

---

## 8. Issue Tracking (Jira Simulation)
**Shared Owners:** `[CV]` & `[GCV]`

> **Directive:** When filing a ticket, the filename must explicitly identify the reporter.

- **Path:** `./docs/jira/*`
- **Naming Convention:** `{ISSUE_TYPE}-{SERIAL_ID}-{REPORTER_AGENT_ID}_{BUG_BRIEF_DESCRIPTION}.md`
    - Example: `BUG-110-GCV_mobile_google_login.md`
    - {SERIAL_ID} must be Decimally-Incremetal
- **Content Requirement:** The file content must strictly state *which agent* discovered the bug.