# Plan Review: Universal MarketCache Migration

## Review Participants
- **[PM] Product Manager**: Validates alignment with user goals.
- **[SPEC] Architect**: Validates technical design and data flow.
- **[DEV] Lead Developer**: Validates feasibility and implementation details.
- **[QA] Quality Assurance**: Validates testability and acceptance criteria.

## Feedback Summary

### [PM] Assessment
- **Alignment:** The plan perfectly addresses the "Close the situation" goal. It removes the dependency on the brittle legacy crawlers.
- **Gap:** The "Comparison Tab" UI needs clear data visualization. The backend plan supports it, but ensure the API returns data in a grid-friendly format (ag-grid or similar).
- **Approved.**

### [SPEC] Assessment
- **Architecture:** Moving `ROICalculator` to `app/services` is the right move. Dependency injection of `MarketDataService` into `StrategyService` ensures a Single Source of Truth.
- **Performance:** `MarketCache` loading implementation (100MB RAM) is acceptable for the server side. `StrategyService` should use standard Python processing (Pandas) which is fast enough for 2000 stocks if data is in memory.
- **Approved.**

### [DEV] Assessment
- **Refactoring:** Moving `calculator.py` is straightforward.
- **Mars Migration:** `strategies/mars.py` logic (filters, ranking) needs to be ported carefully. The "Patch" logic (hardcoded dividends for 2330, 0050) in `mars.py` should potentially be moved to `DividendCache` or a config file, rather than hardcoded in the service. *Action item: Consider moving patches to a configuration.*
- **Backfill:** `yfinance` batch download is reliable.
- **Approved.**

### [QA] Assessment
- **Verification:** The TSMC 22.2% CAGR test is a solid "Golden Master" test.
- **Real-time:** We need to verify that "Today's" data is actually from `yfinance` live fetch. We can mock `yfinance` in tests to return a specific price and assert the service returns it.
- **Approved.**

## Conclusion
The plan is solid. Proceed to PRD generation.
