# Ultra-Fast Crawler - Multi-Agent Design Review

> **Date:** 2026-02-08
> **Subject:** `docs/plans/2026-02-08-ultra-fast-crawler-PRD.md` + Implementation Plan

---

## Phase 1: Primary Designer (Understanding Lock)

**Design Summary:**
- Replace sequential 1-stock-at-a-time crawling with batch+parallel processing
- Use yfinance for ALL price/dividend data (simple, no API keys, no blocking)
- Stock lists from ISIN (TWSE) and TPEx API (O(1) fetch)
- Architecture: asyncio + ThreadPoolExecutor (4 workers) + 200-ticker batches
- Target: <15 min cold run vs current 30-60 min

**Key Decisions Made:**
1. yfinance over direct TWSE/TPEx API (simpler, 2000+ data support)
2. Batch size 200 (yfinance handles well)
3. 4 concurrent workers (balance parallelism vs rate limiting)
4. JSON-only storage (per existing policy)

**Understanding Lock: ✅ CONFIRMED**

---

## Phase 2: Structured Review

### 2.1 Skeptic / Challenger Agent

> *"Assume this design fails in production. Why?"*

**Objections:**

| # | Objection | Assumption Challenged |
|---|-----------|----------------------|
| S1 | **Rate Limiting Risk**: yfinance may throttle or block after many requests. What's the failure mode? | Assumes Yahoo never blocks |
| S2 | **Memory Explosion**: Loading 1959 tickers × 26 years × 6 columns into one DataFrame may exhaust RAM | Assumes RAM is unlimited |
| S3 | **Network Failure Handling**: What happens if batch 5/10 fails mid-crawl? Is state lost? | Assumes network is reliable |
| S4 | **Duplicate Data Risk**: Running twice may overwrite good data with partial data | No atomic writes |

**Designer Response:**
- S1: Will implement exponential backoff and retry logic
- S2: Process in chunks, write to disk after each batch (streaming mode)
- S3: Add checkpoint/resume capability - save progress after each batch
- S4: Use temp files, atomic rename only on success

---

### 2.2 Constraint Guardian Agent

> *"Does this design violate performance, security, or reliability constraints?"*

**Objections:**

| # | Constraint | Issue |
|---|-----------|-------|
| G1 | **Disk Space**: Daily OHLCV for 2000 stocks × 26 years = ~50M rows. JSON size? | May exceed acceptable limits |
| G2 | **CPU Bound**: ThreadPoolExecutor won't help if bottleneck is yfinance parsing | Misidentified bottleneck |
| G3 | **Zeabur Memory**: If MarketCache loads all this at startup, OOM on Zeabur? | Production OOM risk |

**Designer Response:**
- G1: Estimated 300MB total (acceptable per existing policy - JSON < 300MB)
- G2: yfinance is I/O bound (network fetches), not CPU bound - ThreadPool is correct
- G3: Already addressed in existing MarketCache design - lazy load if needed

---

### 2.3 User Advocate Agent

> *"Does this design serve the end user well?"*

**Objections:**

| # | Issue | Impact |
|---|-------|--------|
| U1 | **Cold Start UX**: If cold run takes 15 min, new users wait 15 min? | Bad first experience |
| U2 | **No Progress Visibility**: User sees nothing during crawl | Feels broken |
| U3 | **Stale Data**: If crawl fails silently, user sees old data | Misleading |

**Designer Response:**
- U1: Cold run is one-time ops script, not user-facing. Pre-crawled data ships with deployment.
- U2: Add progress logging (already in plan)
- U3: Add timestamp/version file to indicate data freshness

---

## Phase 3: Integration & Arbitration

### Arbiter Decision Matrix

| Objection | Accept/Reject | Resolution |
|-----------|---------------|------------|
| S1 Rate Limiting | **ACCEPT** | Add retry with exponential backoff |
| S2 Memory | **ACCEPT** | Stream-process batches, don't hold all in RAM |
| S3 Network Failure | **ACCEPT** | Add checkpoint/resume |
| S4 Duplicate Data | **ACCEPT** | Use atomic file writes |
| G1 Disk Space | **REJECT** | 300MB is within policy |
| G2 CPU Bound | **REJECT** | I/O bound analysis is correct |
| G3 Zeabur OOM | **ACCEPT** | Add lazy-load fallback in MarketCache |
| U1 Cold Start | **REJECT** | Ops script, not user-facing |
| U2 Progress | **ACCEPT** | Already in plan |
| U3 Stale Data | **ACCEPT** | Add version/timestamp file |

---

## Decision Log

| Decision | Alternatives | Objections | Resolution |
|----------|-------------|------------|------------|
| Use yfinance for all data | Direct TWSE/TPEx API | Rate limiting risk | Add retry logic |
| Batch size 200 | 50, 100, 500 | Memory risk | Stream-process, don't buffer all |
| 4 workers | 2, 8, 16 | Rate limiting | Start conservative, can tune |
| JSON storage | Parquet, SQLite | Disk space | Within 300MB policy |

---

## Exit Criteria Checklist

- [x] Understanding Lock completed
- [x] Skeptic agent invoked (4 objections)
- [x] Constraint Guardian invoked (3 objections)
- [x] User Advocate invoked (3 objections)
- [x] All objections resolved or rejected with rationale
- [x] Decision Log complete
- [x] Arbiter declared design acceptable

---

## FINAL DISPOSITION: ✅ APPROVED

**Rationale:** Design is sound with accepted modifications:
1. Add retry with exponential backoff
2. Stream-process batches (don't hold all in RAM)
3. Add checkpoint/resume for failure recovery
4. Add data version/timestamp file
5. Consider lazy-load for MarketCache if OOM on Zeabur

**Proceed to implementation with these enhancements.**
