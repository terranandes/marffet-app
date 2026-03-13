# Auth & Database Architecture (Post-Recovery)
**Date**: 2026-03-13
**Version:** 2.0
**Status:** Stable / Production-Ready

This document outlines the authentication, session management, and access control architecture for the Marffet Investment System.

## 1. Authentication Architecture (Dual-UI Support)

We support two distinct UIs accessing the same Backend Logic:
1.  **Next.js Frontend**: `marffet-app.zeabur.app` (Port 3000 locally)
2.  **Legacy Backend UI**: `marffet-api.zeabur.app` (Port 8000 locally)

### The Cookie Strategy
- **Problem**: Enforcing `Domain=marffet-app.zeabur.app` breaks the Legacy UI (Cross-Domain).
- **Solution**: We use `COOKIE_DOMAIN = None` (Host Only).
    - When User visits `marffet-app`, cookie is set for `marffet-app` (valid).
    - When User visits `marffet-api`, cookie is set for `marffet-api` (valid).
    - **Result**: Both UIs work independently.

### The Rewrite Code Flow
To prevent CORS issues and "Third-Party Cookie" blocks:
1.  Frontend uses **Relative Links** (`/auth/login`, `/auth/logout`).
2.  Next.js Rewrites (`next.config.ts`) proxy these requests to the Backend.
3.  The User remains on the Frontend Domain (Difference hidden by proxy).
4.  Cookies are set on the Frontend Domain (First-Party).

---

## 2. Database Self-Healing Strategy (The "User Concern")

We use a **"Startup Migration"** pattern to ensure the database schema on Zeabur (Persistent Volume) is always up-to-date with the code.

### How it Works
On every application startup (`lifespan` in `main.py` -> `init_db` in `portfolio_db.py`), we execute:

```python
try:
    cursor.execute("ALTER TABLE users ADD COLUMN auth_provider ...")
except:
    pass # Column already exists
```

### Addressing Performance Concerns
**Q: Does this inspect the whole database every time?**
**A: NO.**
- SQLite's `ALTER TABLE ADD COLUMN` is an **O(1) operation** (Constant Time).
- It typically modifies the Schema Metadata only. It does **not** rewrite the table rows.
- If the column exists, the statement fails immediately (Microseconds).
- **Impact**: Zero. The server start time is unaffected, regardless of database size.

### Safety
- **Non-Destructive**: `ADD COLUMN` never deletes data.
- **Idempotent**: Running it 100 times has the same effect as running it once.

## 3. Deployment & Recovery
- **Codebase**: `master` branch is the source of truth.
- **Database**: 
    - **Local**: `app/portfolio.db` (Git-tracked seed).
    - **Remote**: `/data/portfolio.db` (Persistent Volume).
- **Sync**: When new code (with new columns) is pushed, Zeabur rebuilds -> App Starts -> `init_db` runs -> Missing columns are added to `/data/portfolio.db` automatically.

**Conclusion:** The system is robust, self-healing, and performant.

## 4. Access Tier Matrix — Complete 5-Tier Model

The backend enforces a strict **5-tier access model** with precedence: `GM > VIP > PREMIUM > FREE > Guest`.

### 4.1 Tier Definitions

| Tier | Auth | Assignment Method | Identity |
|:-----|:-----|:-----------------|:---------|
| **Guest** | None (unauthenticated) | Automatic | `id: "guest"`, `email: "guest@local"`, `is_guest: true`. **Architecture**: Data strictly in `localStorage`. No backend DB persistence. |
| **FREE** | Google OAuth | Automatic on sign-up | Registered Google user, no tier assignment |
| **PREMIUM** | Google OAuth | `PREMIUM_EMAILS` env var or DB injection | Subscriber-level access |
| **VIP** | Google OAuth | `VIP_EMAILS` env var or DB injection | Honor tier for top supporters |
| **GM** | Google OAuth | `GM_EMAILS` env var **only** | Game Master — full admin powers |

### 4.2 Feature Access Matrix

| Feature | Guest | FREE | PREMIUM | VIP | GM |
|:--------|:------|:-----|:--------|:----|:---|
| Mars Strategy Simulator | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bar Chart Race | Basic | Basic | Advanced (CAGR) | Advanced (CAGR) | Advanced (CAGR) |
| Compound Interest (Single) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Compound Interest (Comparison) | 🔒 | 🔒 | ✅ | ✅ | ✅ |
| Portfolio Groups | 3 max | 11 max | 30 max | 30 max | 30 max |
| Targets per Group | 10 max | 50 max | 200 max | 200 max | 200 max |
| Transactions per Target | 10 max | 100 max | 1,000 max | 1,000 max | 1,000 max |
| AI Copilot | ❌ | 🎓 Educator | 💼 Wealth Manager | 💼 Wealth Manager | 💼 Wealth Manager |
| CB Notifications | ❌ | ❌ | ✅ In-App | ✅ In-App + Email | ✅ In-App + Email |
| Rebalancing Alerts | ❌ | ❌ | ✅ In-App | ✅ In-App + Email | ✅ In-App + Email |
| Data Export | ❌ | 📦 Unfiltered | 📥 Filtered + 📦 Unfiltered | 📥 Filtered + 📦 Unfiltered | 📥 Filtered + 📦 Unfiltered |
| Server-Side Data | ❌ (localStorage only) | ✅ | ✅ | ✅ | ✅ |
| Admin Dashboard | ❌ | ❌ | ❌ | ❌ | ✅ |
| Membership Injection | ❌ | ❌ | ❌ | ❌ | ✅ |
| System Operations | ❌ | ❌ | ❌ | ❌ | ✅ |
| Priority Support | ❌ | ❌ | ❌ | ✅ | ✅ |
| Early Access Features | ❌ | ❌ | ❌ | ✅ | ✅ |

### 4.3 Tier Precedence & Resolution Logic

```python
# auth.py — Tier Resolution
tier_levels = {'FREE': 0, 'PREMIUM': 1, 'VIP': 2, 'GM': 3}

# Static config tier (from env vars — immutable)
static_tier = 'GM'      if email in GM_EMAILS
             else 'VIP'      if email in VIP_EMAILS
             else 'PREMIUM'  if email in PREMIUM_EMAILS
             else 'FREE'

# Injected config tier (from user_memberships table — mutable, expirable)
db_tier = injected_tier if valid_until > now() else 'FREE'

# Effective tier = max(static, injected)
tier = max(static_tier, db_tier, key=lambda t: tier_levels[t])

# Premium flag (used by frontend gating)
is_premium = tier in ['PREMIUM', 'VIP', 'GM']
```

### 4.4 Environment Variables

| Env Var | Role | Powers |
|:--------|:-----|:-------|
| `GM_EMAILS` | Admin (Game Master) | Full admin panel + all premium features |
| `VIP_EMAILS` | VIP User | All premium features + priority support + early access |
| `PREMIUM_EMAILS` | Premium User | Premium features only (no admin panel) |
| *(none)* | Free User | Standard features |
| *(not logged in)* | Guest | localStorage-only, limited features |

Format: Comma-separated, case-insensitive. E.g., `PREMIUM_EMAILS=user1@gmail.com,user2@gmail.com`

### 4.5 Dynamic Membership Injection

The GM can manually inject memberships via the Admin Dashboard:

| Field | Options |
|:------|:--------|
| **Email** | Valid Google account email |
| **Tier** | `VIP` or `PREMIUM` |
| **Duration** | Monthly (30d), Annually (365d), Permanent (99y) |

- Injected memberships are stored in `portfolio.db` → `user_memberships` table.
- If an injected membership expires, the user gracefully reverts to their static tier (from env vars) or FREE.
- Static env vars always take precedence over injected tiers of equal or lower rank.

### 4.6 Frontend Sync

- On login, `Sidebar.tsx` reads `/me` response → sets `localStorage("marffet_premium")` if `is_premium` is true.
- `SettingsModal.tsx` shows "⭐ Premium Active" badge for non-admin premium users.
- Premium status is **server-authoritative** — `localStorage` is a convenience cache, not the source of truth.
- The `tier` string is returned by `/auth/me` and can be used for UI-level gating.

### 4.7 Sponsorship Flow

1. User visits **Settings** ⚙️ → **Sponsor Us** tab.
2. Sponsors via [Ko-fi](https://ko-fi.com/terranandes) or [Buy Me a Coffee](https://buymeacoffee.com/terranandes).
3. GM manually injects VIP or PREMIUM membership via Admin Dashboard.
4. User's `/auth/me` response immediately reflects the upgraded tier.

### Deployment
- `GM_EMAILS`, `VIP_EMAILS`, and `PREMIUM_EMAILS` must be configured in Zeabur backend env vars (`.env` is gitignored).
