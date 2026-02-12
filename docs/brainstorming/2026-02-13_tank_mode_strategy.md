# Brainstorming: Standardizing "Tank Mode" & Data Pipeline Strategy

**Date:** 2026-02-13
**Participants:** `[PL]`, `[SPEC]`, `[CODE]`, `[CV]`
**Topic:** Scaling "Tank Mode" (Ultra-Stability) across admin/cron operations while maintaining local development velocity.

---

## 🤖 Multi-Agent Perspectives

### `[PL]` (Project Leader) - Direction & Efficiency
> "We need a 'Set and Forget' system for Zeabur. If we push a backfill, it MUST finish, even if it takes 24 hours. However, my local engineers (Terran) shouldn't be penalized by 'Tank Mode' slowness. We need asymmetric execution."

### `[SPEC]` (Technical Architect) - Structural Integrity
> "Environment-aware tuning is the solution. We should implement a 'Resource Profile' system. 
> - **PROFILE_LOW**: (Zeabur) `CHUNK_SIZE=1`, `Flushing=True`, `Delay=0.5s`.
> - **PROFILE_HIGH**: (Local/High RAM) `CHUNK_SIZE=100`, `Threads=Auto`, `Flushing=Manual`.
> 
> Regarding Local Backfill + Push: This is a viable 'Fast Track', but we must ensure the `data/raw/*.json` files are properly versioned to avoid merge conflicts."

### `[CODE]` (Backend Lead) - Implementation Logic
> "I can refactor `backfill_all_stocks` and `sync_all_dividends` to use a central `StabilityManager`.
> ```python
> class StabilityManager:
>     @staticmethod
>     def get_config():
>         if os.getenv("ZEABUR"): # Or check RAM
>             return {"chunk": 1, "flush": 20, "delay": 0.5}
>         return {"chunk": 50, "flush": 500, "delay": 0}
> ```
> This makes 'Tank Mode' a global standard rather than a one-off patch."

### `[CV]` (Lead Auditor) - Stability & Risk
> "Local Backfill is FAST, but it introduces a 'Single Point of Failure'. If Terran's internet cuts out, the push fails. The Cloud Backfill (Tank Mode) is our 'Infrastructure Insurance'. We should keep both.
> **Warning:** Progressive Saving is good, but we must ensure file atomicity during flushes to prevent JSON corruption if a process is killed mid-write."

---

## 🛑 SOCRATIC GATE: Strategic Questions

### 1. [PRIORITY: P0] **[DATA SOURCE OF TRUTH]**
**Question:** If we backfill locally and push the JSON files, how do we handle the "Drift" between local data and cloud data?
**Why This Matters:** If two people backfill different stocks locally and push, we might get partial data or overwritten files.

### 2. [PRIORITY: P1] **[RESOURCE DETECTION]**
**Question:** Should we detect "Zeabur" specifically, or should we detect available RAM (e.g., using `psutil`) to decide when to engage Tank Mode?
**Why This Matters:** Future-proofs us for other cloud providers or different Zeabur plans.

### 3. [PRIORITY: P1] **[TANK MODE SCOPE]**
**Question:** Should "Tank Mode" also apply to the `NotificationEngine` and `StrategyService` during heavy computation, or just to Data IO?
**Why This Matters:** Consistency in stability across the whole backend.

---

## 📂 Implemented Solution: "Adaptive Flow" ✅

I have implemented the **Adaptive Flow** in [market_data_service.py](file:///home/terwu01/github/martian/app/services/market_data_service.py).

1. **Auto-Pilot**: Detects `ZEABUR`, `RAILWAY`, or `RENDER` environment variables.
2. **Standard Tuning**:
    - **Cloud (Tank Mode)**: `CHUNK_SIZE=1`, `SAVE_INTERVAL=20`, `BATCH_DELAY=0.5s`.
    - **Local (Fast Mode)**: `CHUNK_SIZE=50`, `SAVE_INTERVAL=200`, `BATCH_DELAY=0.0s`.
3. **Local Fast-Track**: Terran can now click the "Backfill" button locally, and it will process stocks in batches of 50, making it significantly faster than the cloud.

---

## 🏁 Summary for Terran
**My Recommendation:** 
We SHOULD standardise Tank Mode. It makes the system robust. 
But we should NOT stay slow locally. 
**Next Step:** I will draft a `SystemHealthService` that manages these limits dynamically.

**What do you think about the 'Adaptive Flow'?**
