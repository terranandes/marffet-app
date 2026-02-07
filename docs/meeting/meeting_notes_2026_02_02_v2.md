# Meeting Notes: 2026-02-02 (v2) - Phase 2 Emergency Sync

**Date**: 2026-02-02 23:05
**Participants**: [PM], [PL], [SPEC], [CODE], [CV], [UI]
**Topic**: Critical Data Discrepancy & Phase 2 Kickoff

---

## 1. 🚨 Critical Incident: The "$193M vs $86M" Hallucination

**[CV] Reporting**:
- **Observation**: Martian's simulation for TSMC (2330) generated **$193M** wealth vs MoneyCome's **$86M**.
- **Root Cause**: **Data Source Poisoning**.
    - We used `yfinance` default "Adjusted Prices" (Start Price ~$29).
    - Real 2006 Price was ~$60.
    - **Effect**: Initial share purchase was inflated by **~200%**.
- **Conclusion**: The simulation engine is mathematically sound, but the *Input Data* is incompatible with "Explicit Dividend Reinvestment" logic. You cannot reinvest dividends if the price history *already* assumes they were reinvested (double counting).

## 2. 🛠️ Pivot Decision: Phase 2 Scraper (P0)

**[PM] Directive**:
- User explicitly requested **Accuracy** over Features.
- **Decision**: Stop Multi-language. Start **Phase 2 Scraper** immediately.

**[CODE] Technical Insight**:
- **Discovery**: `yfinance(auto_adjust=False)` *does* return Unadjusted Data (~$59 confirmed in probe). 
- **Strategy**: 
    1.  **Short Term**: We *could* re-ingest using `yfinance` unadjusted to fix the Listed stocks immediately.
    2.  **Long Term**: Build the **Official TWSE Scraper** (Legacy Endpoint) to capture the missing 658 Emerging/Delisted stocks and guarantee 100% authority.
- **Consensus**: We will proceed with the **Official Scraper** as requested to ensure we own the data pipeline and solve the "Missing Stocks" issue simultaneously.

## 3. 📊 Project Status

| Module | Status | Notes |
| :--- | :--- | :--- |
| **Mars Strategy** | ⚠️ **Data Blocked** | Logic done. Metrics blocked by Data Quality. |
| **Data Lake** | 🟡 **Partial** | 99% Coverage of Main List, but Price Quality is FAILED (Adjusted). |
| **Compound UI** | ✅ **Ready** | De-branded. Placeholder added. Mobile responsive. |
| **Cash Ladder** | ✅ **Ready** | Leaderboard functional. |

## 4. 📝 Action Items

1.  **[CODE]**: Reverse Engineer TWSE Legacy API (FMT8) or HTML parsing for 2006-2026 history.
2.  **[CODE]**: Build `tests/ops_scripts/crawl_official.py`.
3.  **[CV]**: Define "Data Quality Checks" (e.g., Warning if 2006 price < 40 for TSMC).
4.  **[PL]**: Update `tasks.md` to reflect P0 Scraper.

---

**Signed**,
[PL] - Project Leader
