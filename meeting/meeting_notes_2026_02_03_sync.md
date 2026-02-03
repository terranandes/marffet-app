# Meeting Notes: Agents Sync-Up
**Date**: 2026-02-03
**Version**: v2 (Post-Phase 3)
**Participants**: [PM], [PL], [SPEC], [CODE], [UI], [CV]

---

## 1. Project Progress & Strategy
**[PM] Product**:
-   **Status**: GREEN. The "Clean Room" strategy is a massive success. eliminating the "Excel Dependency" removes a huge failure point.
-   **Win**: Verified TSMC (2330) CAGR is **18.8%** (Realistic) vs the previous ~200M hallucination. We can trust the engine now.
-   **Pivot**: Accepted "Survivorship Bias" (dropping delisted stocks) to prioritize "Current Wealth Simulation".

**[PL] Project Lead**:
-   **Phase 2 (Scraper)**: Completed.
-   **Phase 3 (Integration)**: Completed. `MarketCache` is deployed.
-   **Phase 4 (Daily Data)**: **IN PROGRESS**. Scraper (PID 70948) is currently fetching Daily OHLCV to support "Trend" and "Race" tabs.
-   **Metrics**: Cold Load 0.15s. Hot Query 0.00s.

---

## 2. Technical Architecture
**[SPEC] Architect**:
-   **Data Lake**: We settled on **JSON Files (Nested Schema V2)**.
    -   *Why*: At ~300MB, it fits entirely in RAM. No need for Postgres/DuckDB yet.
-   **Policy**: Enforced "Single Source (Crawler) -> Single Cache (RAM) -> All Features". Documented in `product/universal_data_cache_policy.md`.

**[CODE] Backend**:
-   **Achievement**: Refactored `ROICalculator` to handle the new V2 Schema (`node['summary']` vs `node`). Backward compatibility maintained.
-   **Next**: Once the crawler finishes, I need to update the `/trend` and `/race` endpoints to consume `node['daily']` for smoother animations.

---

## 3. Deployment & Bugs
**[UI] Frontend**:
-   **Feedback**: The "Compound Interest" tab is instant now. Huge improvement over the 3s latency.
-   **Mobile**: Sidebar layout is stable.
-   **Pending**: The "Trend" chart is still using yearly points. Waiting for Phase 4 daily data to make it high-res.

**[CV] Quality**:
-   **Bug Triage**:
    -   *Fixed*: TSMC split-adjusted price bug (via `auto_adjust=False`).
    -   *Fixed*: JSON I/O Latency (via `MarketCache`).
    -   *Watchlist*: Scraper error handling. I see some `ERROR - $6904.TW: possibly delisted` in the logs. This is expected but should be monitored.

---

## 4. Features & Roadmap
| Feature | Status | Owner |
| :--- | :--- | :--- |
| **Clean Room Scraper** | ✅ Done | [CODE] |
| **Market Cache (RAM)** | ✅ Done | [CODE] |
| **Comp. Interest Tab** | ✅ Done | [UI] |
| **Universal Lake (Daily)** | 🔄 Running | [PL] |
| **Trend/Race Upgrade** | ⏳ Pending Data | [UI] |
| **Scientific Backtest** | ⏸️ Deferred | [PM] |

---

## 5. Summary
The system is stable, fast, and accurate. We are currently "refueling" the data lake with high-resolution fuel (Daily Data) for the next visual upgrade.

**Signed**,
*[PL] Project Leader*
