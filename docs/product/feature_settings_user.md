# Settings Modal & User System — Feature Specification

**Date**: 2026-02-17
**Owner**: [SPEC] Agent
**Status**: Production

---

## 1. Overview

The **Settings Modal** is a global overlay accessible from the sidebar on every page. It provides profile management, app preferences, AI key configuration, help/documentation, and a feedback/support system. It is **not a route** — it is a modal component rendered by the `Sidebar`.

---

## 2. Tabs

### 2.1 Profile (👤)

| Feature              | Description                                         |
|:-------------------- |:--------------------------------------------------- |
| **Avatar + Name**    | Displays Google profile picture, name, and email    |
| **Admin Badge**      | Shows 👑 "Game Master" badge for admin users        |
| **Nickname**         | Editable display name for the leaderboard           |
| **Leaderboard Sync** | "Sync Now" button to update wealth stats on ladder  |

**Endpoints Used**:
- `POST /api/auth/profile` — Update nickname
- `POST /api/portfolio/sync-stats` — Sync leaderboard stats

### 2.2 Preferences (🌍)

| Feature             | Storage       | Description                             |
|:------------------- |:------------- |:--------------------------------------- |
| **Start Page**      | localStorage  | Default landing page (Dashboard/Portfolio/Mars/Viz/CB) |
| **Region**          | localStorage  | Fixed to Taiwan (TW). CN/US planned Q4 2026 |
| **GM Controls**     | localStorage  | Premium status toggle (admin-only)      |

**Key**: All preferences saved to `localStorage` with `martian_` prefix.

### 2.3 AI Keys (🔑)

| Feature           | Storage       | Description                                |
|:----------------- |:------------- |:------------------------------------------ |
| **Gemini API Key** | localStorage | Override server default key for higher rate limits |

**Key**: `martian_api_key` in localStorage

### 2.4 Help (📚)

| Feature           | Description                                         |
|:----------------- |:--------------------------------------------------- |
| **Documentation** | Link to `/doc` page                                 |
| **Feature Guide** | Accordion with brief descriptions of all features   |
| **Premium List**  | Accordion showing premium-only features and limits  |

### 2.5 Support (💬)

| Feature             | Description                                       |
|:------------------- |:------------------------------------------------- |
| **Email Support**   | `mailto:support@martian.com` link                 |
| **Feedback Form**   | Type (suggestion/bug/question) + Category + Message |

**Feedback Categories**:
Settings, Subscription, Mars Strategy, Bar Chart Race, Portfolio, Trend, My Race, AI Copilot, Leaderboard, Other

**Endpoint**: `POST /api/feedback`

---

## 3. Frontend

**Component**: `frontend/src/components/SettingsModal.tsx` (584 lines)
**Triggered By**: Sidebar ⚙️ gear icon

### Key Functions

| Function              | Purpose                                         |
|:--------------------- |:----------------------------------------------- |
| `handleSaveProfile()` | POST nickname to `/api/auth/profile`            |
| `handleSyncStats()`   | POST to `/api/portfolio/sync-stats`             |
| `handleSavePreferences()` | Save start page, region, premium to localStorage |
| `handleSaveKey()`     | Save Gemini API key to localStorage             |
| `handleSendFeedback()` | POST feedback to `/api/feedback`               |

---

## 4. User System Backend

### Authentication

**File**: `app/auth.py`

| Method | Endpoint            | Description                          |
|:------ |:------------------- |:------------------------------------ |
| `GET`  | `/auth/login`       | Redirect to Google OAuth             |
| `GET`  | `/auth/callback`    | Handle OAuth callback, create session|
| `GET`  | `/auth/me`          | Return current user from session     |
| `POST` | `/auth/guest`       | Create anonymous guest session       |
| `POST` | `/auth/logout`      | Clear session cookie                 |

### User Settings

**Router**: `app/routers/user.py`
**Prefix**: `/api/user`

| Method | Endpoint           | Description                          |
|:------ |:------------------ |:------------------------------------ |
| `GET`  | `/api/user/settings` | Get user preferences + API key     |
| `POST` | `/api/user/settings` | Save preferences + optional API key|

### User Feedback

**File**: `app/feedback_db.py`

| Method  | Endpoint                  | Auth    | Description                    |
|:------- |:------------------------- |:------- |:------------------------------ |
| `POST`  | `/api/feedback`           | Session | Submit feedback                |
| `GET`   | `/api/feedback`           | Admin   | List all feedback              |
| `GET`   | `/api/feedback/stats`     | Admin   | Feedback counts by status      |
| `GET`   | `/api/feedback/categories`| None    | Available feedback categories  |
| `PATCH` | `/api/feedback/{id}`      | Admin   | Update status / agent notes    |

---

## 5. Sidebar Component

**File**: `frontend/src/components/Sidebar.tsx` (493 lines)

### Features

1. **Navigation Links** — All app pages with icons and active state
2. **User Info** — Avatar, name, admin badge
3. **Login/Logout** — Google OAuth or Guest mode
4. **Notifications Bell** — Badge count + dropdown list
5. **Settings Gear** — Opens SettingsModal
6. **Data Timestamp** — Shows last data refresh time
7. **Collapsible** — Responsive sidebar with mobile toggle

### Navigation Items

| Label           | Route        | Icon | Access    |
|:--------------- |:------------ |:---- |:--------- |
| Dashboard       | `/`          | 🏠   | All       |
| Mars Strategy   | `/mars`      | 🚀   | All       |
| BCR Race        | `/viz`       | 📈   | All       |
| Portfolio       | `/portfolio` | 💼   | Logged in |
| Trend           | `/trend`     | 📊   | Logged in |
| My Race         | `/myrace`    | 🏎️   | Logged in |
| Compound        | `/compound`  | 🧪   | All       |
| CB Strategy     | `/cb`        | 💹   | Logged in |
| Leaderboard     | `/ladder`    | 🏆   | All       |
| Admin           | `/admin`     | ⚙️   | Admin     |
| Doc             | `/doc`       | 📚   | All       |

---

## 6. Notification System

**Endpoint**: `GET /api/notifications`
**Engine**: `app/engines/` → `NotificationEngine`

The notification system generates alerts based on:
- Portfolio stock price movements
- CB premium threshold crossings
- System events (data refresh completed, etc.)

Notifications appear as a bell icon badge in the sidebar with a dropdown panel.
