# Guest Mode Architecture: Multi-Agent Review

**Date:** 2026-03-13
**Source:** `guest_mode_architecture_analysis.md`
**Status:** REVIEW IN PROGRESS

---

## Phase 1 Summary (From Primary Designer)

The Primary Designer (`[PL]`) discovered that Guest Mode has a **dual implementation** with a design disconnect:

- **Mode A (Active):** Backend Guest — user `id='guest'` in SQLite, uses `ApiPortfolioService`, data is shared across all guests
- **Mode B (Dormant):** LocalStorage Guest — `GuestPortfolioService`, only activates when backend is unreachable

The E2E tests were failing because the test assumed LocalStorage mode, but the real flow uses Backend API mode.

**Proposed Options:**

- A: Fix E2E test to verify API calls
- B: Add proper `isGuest` detection
- C: Switch to pure LocalStorage guest
- D: Keep current, test Backend Guest properly (Recommended with B as follow-up)

---

## Phase 2: Structured Review

---

### 2️⃣ Skeptic / Challenger Agent

> "Assume this design fails in production. Why?"

**Objection 1: Shared `user_id='guest'` is a data pollution bomb** 🔴

If two anonymous users are both in "Guest Mode" at the same time, they both read/write to `user_id='guest'` in the DB. User A creates group "My Stocks", User B sees it and deletes it. This is **not a guest experience**, it's a shared anonymous account.

- **Assumption being challenged:** "Guest mode provides a personal demo experience"
- **Impact:** Users may see, modify, or delete each other's data — violating the "Data stored locally only" promise shown in the sidebar UI text

**Objection 2: The Sidebar explicitly says "Data stored locally only"** 🔴

`Sidebar.tsx:382` renders: `<p className="text-xs text-zinc-500 text-center">Data stored locally only</p>`

This is **factually incorrect** in the current implementation. Guest data goes to the backend SQLite DB, not localStorage. This is a UX trust violation.

**Objection 3: The `isGuest` flag never becomes `true` in normal Guest flow** 🟡

`usePortfolioData` sets `isGuest = true` only when the API returns 401/403. Since the guest has a valid session, the API returns 200, so `isGuest` stays `false`. The "Guest Mode" badge in `PortfolioHeader` is **never shown** during normal guest usage.

**Objection 4: `GuestPortfolioService` (500 lines) is dead code** 🟡

The entire `GuestPortfolioService` class with its LocalStorage logic is unreachable during normal guest flow. It only activates if the backend is completely down — an edge case that's essentially "offline mode", not "guest mode".

---

### 3️⃣ Constraint Guardian Agent

**Security & Privacy:**

- 🔴 **Shared user_id='guest'** — Any guest can see/modify/delete any other guest's portfolio data. No data isolation.
- 🟡 **Session persistence** — Guest session cookie has no explicit expiry. A guest could theoretically maintain a long-lived session.

**Maintainability:**

- 🟡 **Two service implementations** (`ApiPortfolioService` + `GuestPortfolioService`) for what's conceptually one feature. Increases maintenance burden.
- 🟡 **Misleading variable names** — `isGuest` doesn't mean what it says. Future developers will be confused.

**Reliability:**

- 🔴 **DB cleanup in E2E tests** deletes ALL guest data. If tests run on a shared staging environment, they'd wipe demo data.

**Performance:**

- ✅ No performance concerns — guest uses the same API path as regular users.

---

### 4️⃣ User Advocate Agent

**Cognitive Load:**

- 🔴 **"Data stored locally only" is a lie.** Users who read this and trust it may store sensitive portfolio data, expecting browser-only privacy. In reality, it's stored on the server.

**Usability:**

- 🟡 **No visual differentiation** — Guest users see exactly the same UI as logged-in users (no "Guest Mode" badge). They can't tell if they're in a limited/temporary mode.

**Error Handling:**

- 🟡 **If two guests create the same group name** — both will succeed but both will see all groups, leading to confusion.

**Intent vs Experience Mismatch:**

- The sidebar says "Explore as Guest" with "Data stored locally only"
- The actual experience is "Shared anonymous backend account with persistent server data"
- This is a **fundamental UX mismatch**

---

## Phase 3: Integration & Arbitration

### 5️⃣ Integrator / Arbiter Agent

**Review of Objections:**

| # | Objection | Severity | Decision | Rationale |
|---|---|---|---|---|
| S1 | Shared `user_id='guest'` data pollution | 🔴 Critical | **ACCEPTED** | This is a real production risk. Must be addressed. |
| S2 | "Data stored locally only" text is false | 🔴 Critical | **ACCEPTED** | UX trust violation. Fix text or fix implementation. |
| S3 | `isGuest` flag never true in normal flow | 🟡 Medium | **ACCEPTED** | Misleading code, but not user-facing danger. |
| S4 | GuestPortfolioService is dead code | 🟡 Medium | **ACCEPTED** | Creates maintenance confusion. |
| C1 | No guest data isolation | 🔴 Critical | **ACCEPTED** | Same as S1. |
| C2 | Session persistence | 🟡 Medium | **DEFERRED** | Not urgent for current scope. |
| U1 | "Data stored locally only" lie | 🔴 Critical | **ACCEPTED** | Same as S2. |
| U2 | No visual Guest differentiation | 🟡 Medium | **ACCEPTED** | Low effort fix. |

### Final Decision

**VERDICT: REVISE — Option D is insufficient. Option C+B is the correct path.**

**Rationale:**
The current implementation has two critical bugs disguised as an architecture choice:

1. **The UI promises "Data stored locally only" but stores data on the server** (S2/U1)
2. **All guests share one DB account, so data bleeds between users** (S1/C1)

The correct implementation should match the stated UX promise: Guest data should be stored in LocalStorage (browser-only), making `GuestPortfolioService` the **active** service for Guest mode, not dead code.

### Recommended Implementation

| Step | Action | Priority |
|---|---|---|
| 1 | **Fix Guest Login:** Remove DB user creation from `/auth/guest`. Guest should NOT get a backend session. | P0 |
| 2 | **Fix usePortfolioData:** When user has `is_guest: true`, use `GuestPortfolioService` explicitly | P0 |
| 3 | **Fix Sidebar text:** Keep "Data stored locally only" (it will be true now) | P0 |
| 4 | **Show Guest Mode badge:** Pass `isGuest` correctly to `PortfolioHeader` | P1 |
| 5 | **Fix E2E test:** Test the LocalStorage-based guest flow | P1 |
| 6 | **OR Alternative:** If shared backend guest is intentional, fix the text to say "Data stored on server" and add per-session isolation | P0-alt |

### ❓ Decision Required from Terran

> **Which path do you want?**
>
> **Path 1:** Guest = LocalStorage (match the current UI promise, activate dead code)
> **Path 2:** Guest = Shared Backend (fix the text, accept data sharing)
> **Path 3:** Guest = Per-session Backend (separate DB groups per guest session — more complex)

---

## Decision Log

| # | Decision | Alternatives | Objections | Resolution |
|---|---|---|---|---|
| D1 | Guest Mode architecture needs clarity | Keep current / Fix text / Fix impl | S1, S2, U1 — shared data + false UI text | PENDING: Terran's decision on Path 1/2/3 |
| D2 | E2E test must match actual architecture | Test LocalStorage / Test API | All previous test failures | Blocked by D1 |
| D3 | `isGuest` flag naming needs fix | Rename to `isOffline` / Fix logic | S3 — misleading | ACCEPTED: will fix regardless of D1 |
