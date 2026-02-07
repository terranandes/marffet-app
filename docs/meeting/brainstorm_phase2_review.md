# Decision Log: Phase 2 Scraper & Architecture Review

**Date**: 2026-02-03 02:20
**Skill Used**: `multi-agent-brainstorming`
**Status**: **CONDITIONAL APPROVAL**

---

## 1. Design Overview (Primary Designer: [PM])
**Objective**: "Clean Room" Data Lake Implementation.
-   **Source**: Official TWSE ISIN (Modes 2 & 4).
-   **Method**: `yfinance(auto_adjust=False)` for unadjusted physics.
-   **Storage**: Yearly JSON Shards (`Market_{YR}.json`).
-   **Scope**: Active Universe Only (Survivorship Bias accepted).

---

## 2. Review Record

### 🤖 Skeptic / Challenger ([CV] Agent)
> *"Assume this design fails. Why?"*

-   **Objection 1 (Coverage / Bias)**:
    -   *Critique*: Eliminating 1436 delisted stocks introduces massive **Survivorship Bias**. Backtesting historical strategies will yield spuriously high results (e.g., buying "All Tech Stocks 2000" ignoring those that died).
    -   *Designer Response*: This tool is primarily for **Current Personal Assets** (Holdings). Users hold surviving stocks.
    -   *Arbiter Decision*: **ACCEPTED (Risk Accepted)**. Warning must be added to "Strategy" UI.

-   **Objection 2 (Clean Room Integrity)**:
    -   *Critique*: `yfinance` is arguably not "Official". It's a third-party aggregator. The "Clean Room" is only partial (List Source is Official, Price Source is Yahoo).
    -   *Designer Response*: True. But scraping TWSE HTML for 20 years of daily data is O(N) heavy/risky (IP Ban).
    -   *Arbiter Decision*: **ACCEPTED**. "Clean Source List" is sufficient for Phase 2.

### 🛡️ Constraint Guardian ([SPEC] Agent)
> *"Enforce Non-Functional Constraints (Speed, Storage, Reuse)."*

-   **Objection 3 (Storage Efficiency)**:
    -   *Critique*: Storing data in **20 separate JSON files** (Yearly) is inefficient. Querying one stock's 20-year history requires **20 File Handles**.
    -   *Constraint*: This violates **Optimized I/O** principles.
    -   *Proposed*: SQLite / DuckDB / Parquet.
    -   *Arbiter Decision*: **REVISE**. JSON is kept for debugging visibility, but **Application Layer MUST implement Caching** (Load Once, Read Memory) to mask this IO cost.

-   **Objection 4 (Reusability)**:
    -   *Critique*: Logic resides in `tests/ops_scripts/crawl_official.py`. It cannot be imported by `app/main.py`. This violates **DRY**.
    -   *Arbiter Decision*: **REVISE**. Logic must be refactored into `app/project_tw/crawler.py`.

### 👤 User Advocate ([UI] Agent)
> *"Represent the End-User Experience."*

-   **Objection 5 (Speed)**:
    -   *Critique*: Loading "Mars Strategy" with 20 file-reads per stock will cause noticeable lag on cheap cloud hosting (Zeabur).
    -   *Arbiter Decision*: **Link to Objection 3**. Caching is mandatory.

---

## 3. Final Decision Log

| ID | Item | Decision | Rationale |
| :--- | :--- | :--- | :--- |
| **D-01** | **Strict Clean Room (ISIN)** | ✅ **APPROVED** | Eliminates "Poisoned Excel" dependency. |
| **D-02** | **Survivorship Bias** | ⚠️ **ACCEPTED RISK** | Documented. Priority is Current Holdings. |
| **D-03** | **JSON Storage** | ❌ **REJECTED (as final)** | Accepted only as "Raw Layer". App must use **Memory Cache** or **Parquet** in Phase 3. |
| **D-04** | **Reusability** | 🔄 **REVISE** | `crawl_official.py` -> `app/services/UniCrawler`. |
| **D-05** | **Optimization** | 🔄 **REVISE** | Implement "Load-All-On-Startup" pattern to solve Speed/IO. |

---

## 4. Disposition
**STATUS**: **PROCEED WITH REVISIONS** (Refactor Script -> Class; Implement Caching).
