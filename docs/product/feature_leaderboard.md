# Leaderboard & Ladder Tabs — Feature Specification

**Date**: 2026-02-17
**Owner**: [SPEC] Agent
**Status**: Production

---

## 1. Overview

The **Leaderboard** (`/ladder`) is a community ranking system where users compete based on their real portfolio performance. Users sync their portfolio stats to appear on the global leaderboard with their nickname, ROI%, and total market value.

---

## 2. Core Concepts

| Concept          | Description                                                     |
|:---------------- |:--------------------------------------------------------------- |
| **Ladder**       | Public ranking of users by market value or ROI                  |
| **Sync Stats**   | User-triggered action to update their cached net worth and ROI  |
| **Public Profile**| Sanitized view of a user's portfolio (no exact positions)      |
| **Nickname**     | Display name on the leaderboard (set via Settings Modal)        |

---

## 3. Frontend

**Route**: `/ladder`
**File**: `frontend/src/app/ladder/page.tsx` (276 lines)

### UI Components

1. **Rank Table** — Top 50 users sorted by market value
   - Rank badge (🥇🥈🥉 for top 3)
   - Avatar, nickname, market value, ROI%, holdings count
   - Color-coded rows for top performers

2. **User Profile Modal** — Click on any user to view:
   - Public portfolio summary
   - Asset allocation breakdown
   - Historical performance (if premium)

3. **Share Button** — `ShareButton` component for sharing rank

### Key Functions

| Function            | Purpose                                  |
|:------------------- |:---------------------------------------- |
| `openProfile(uid)`  | Opens public profile modal for a user    |
| `formatCurrency()`  | Format numbers as TWD currency           |
| `getRankBadge(rank)` | Returns 🥇🥈🥉 or numeric rank         |
| `getRankColor(rank)` | Gold/Silver/Bronze or default coloring  |

---

## 4. Backend API

| Method | Endpoint                         | Auth    | Description                    |
|:------ |:-------------------------------- |:------- |:------------------------------ |
| `GET`  | `/api/leaderboard?limit=50`      | None    | Public leaderboard data        |
| `GET`  | `/api/public/profile/{user_id}`  | None    | Sanitized public profile       |
| `POST` | `/api/portfolio/sync-stats`      | Session | Update user's cached stats     |

### Leaderboard Data Schema

```json
{
    "id": "user_uuid",
    "nickname": "TopG",
    "avatar": "https://...",
    "market_value": 5200000,
    "roi": 42.5,
    "total_cost": 3650000,
    "rank": 1,
    "holdings_count": 12
}
```

---

## 5. Stats Sync Flow

```
User clicks "Sync Now" (Settings Modal)
    │
    └── POST /api/portfolio/sync-stats
            │
            ├── Calculate total market value (all targets × live prices)
            ├── Calculate total cost (sum of all buy transactions)
            ├── Calculate ROI = (value - cost) / cost × 100
            └── Write to user_stats table
                    │
                    └── Appears on GET /api/leaderboard
```

---

## 6. Privacy

- Public profiles show **aggregated** data only (total value, ROI, holdings count)
- Individual stock positions, transaction details, and dividend amounts are **NOT** exposed
- Users must explicitly trigger "Sync Stats" to publish their data
