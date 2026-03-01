# Multi-Language Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add frontend multi-language support (en, zh-TW, zh-CN) powered by a custom React Context + JSON translation files, controlled via the Settings modal Preferences tab.

**Architecture:** Zero-dependency custom i18n using a `LanguageProvider` context that reads the user's language preference from `localStorage` (`martian_lang` key — already exists). JSON translation files per locale are loaded at app init. All pages are `"use client"` components, so no SSR i18n complexity.

**Tech Stack:** React Context API, JSON files, Next.js 16 App Router (client components only)

**Languages:** English (`en`), Traditional Chinese (`zh-TW`), Simplified Chinese (`zh-CN`)

---

## Brainstorming Summary

### Options Evaluated

| Option | Approach | Pros | Cons | Verdict |
|--------|----------|------|------|---------|
| A | `next-intl` | Full Next.js integration, SSR | Requires App Router restructuring, URL-based locales, heavy | ❌ Overkill |
| B | `react-i18next` | Battle-tested, flexible | New dependency, setup overhead for client-only app | ❌ Unnecessary |
| C | **Custom Context + JSON** | Zero-dependency, full control, simple | Manual interpolation | ✅ **Selected** |

### Decision Rationale
- All 11 page routes use `"use client"` — no SSR i18n needed
- `localStorage` preference (`martian_lang`) already exists in SettingsModal (line 51, 72, 126)
- No URL-based locale routing needed (user selects in Settings modal)
- Lean stack (no new npm deps) aligns with project philosophy
- Easy to maintain: add strings by editing JSON files

---

## Proposed Changes

### Phase 1: i18n Infrastructure (Core)

#### [NEW] `frontend/src/lib/i18n/locales/en.json`
English translation strings (~200+ keys) covering: sidebar labels, settings modal, toast messages, page headers, table headers, buttons, and common labels.

#### [NEW] `frontend/src/lib/i18n/locales/zh-TW.json`
Traditional Chinese (繁體中文) translation of all keys from `en.json`.

#### [NEW] `frontend/src/lib/i18n/locales/zh-CN.json`
Simplified Chinese (简体中文) translation of all keys from `en.json`.

#### [NEW] `frontend/src/lib/i18n/LanguageContext.tsx`
- `LanguageProvider` component wrapping the app
- `useTranslation()` hook returning `t(key, params?)` function
- `useLanguage()` hook returning `{ language, setLanguage }` for the Settings dropdown
- `t(key, { count, total })` interpolation support: replaces `{count}` in strings with variable values
- Fallback: missing key in current locale → falls back to `en.json` → falls back to the key itself

---

### Phase 2: Wiring the Language Selector

#### [MODIFY] `frontend/src/components/ClientProviders.tsx`
- Wrap existing providers with `<LanguageProvider>`

#### [MODIFY] `frontend/src/components/SettingsModal.tsx`
- Add a Language dropdown UI in the Preferences tab (currently the `language` state exists at line 51 but no dropdown is rendered)
- Show flag icons + native language names: 🇺🇸 English, 🇹🇼 繁體中文, 🇨🇳 简体中文
- Wire dropdown change to `useLanguage().setLanguage()` context + `localStorage`
- Replace hardcoded strings in SettingsModal with `t()` calls

#### [MODIFY] `frontend/src/components/Sidebar.tsx`
- Replace hardcoded menu labels ("Mars Strategy", "Bar Chart Race", "Portfolio", etc.) with `t()` calls
- Replace "Sign Out", "Sign In with Google", notification text

---

### Phase 3: Page-by-Page String Extraction

#### [MODIFY] All page files:
- `src/app/page.tsx` — Dashboard
- `src/app/mars/page.tsx` — Mars Strategy
- `src/app/compound/page.tsx` — Compound Interest
- `src/app/portfolio/` — Portfolio pages (11 files)
- `src/app/trend/page.tsx` — Trend
- `src/app/ladder/page.tsx` — Cash Ladder
- `src/app/race/page.tsx` — Bar Chart Race
- `src/app/myrace/page.tsx` — My Race
- `src/app/cb/page.tsx` — Convertible Bond
- `src/app/viz/page.tsx` — Visualizations
- `src/app/admin/page.tsx` — Admin Dashboard
- `src/app/doc/page.tsx` — Documentation

Replace hardcoded English strings with `t('key')` calls. Financial data, stock names, and numbers remain untranslated.

#### [MODIFY] Other components:
- `src/components/AICopilot.tsx` — UI labels
- `src/components/DataTimestamp.tsx` — "Data as of" text
- `src/components/StockDetailModal.tsx` — Modal labels
- `src/components/ShareButton.tsx` — Button text
- `src/components/StrategyCard.tsx` — Card labels
- `src/components/Skeleton.tsx` — Loading text (if any)

---

### Phase 4: Layout Integration

#### [MODIFY] `frontend/src/app/layout.tsx`
- Dynamic `<html lang={...}>` attribute based on selected language (may require a thin client wrapper)

---

## Verification Plan

### Automated Tests
No existing frontend unit tests found in this project. Verification will be manual + Playwright MCP.

### Visual Verification (Playwright MCP)
1. Navigate to `http://localhost:3000`
2. Click the ⚙️ Settings gear icon
3. Go to "Preferences" tab
4. Change language to "繁體中文"
5. Verify Sidebar labels change to Chinese (e.g., "火星策略", "投資組合")
6. Close Settings → Navigate to `/mars` → Verify page header is in Chinese
7. Switch to "简体中文" → Verify Sidebar and page use simplified characters
8. Switch back to "English" → Verify everything reverts

### Manual Verification (Boss Review)
- Boss (Terran) reviews all 3 languages in the Settings modal
- Boss verifies the language persists across page refresh (localStorage)
- Boss checks that financial data (stock names, prices, percentages) remain untranslated

---

## String Count Estimate

| Area | Est. Strings | Priority |
|------|-------------|----------|
| Sidebar menu labels | ~15 | Phase 2 |
| Settings Modal (5 tabs) | ~60 | Phase 2 |
| Toast messages | ~20 | Phase 2 |
| Mars Strategy page | ~30 | Phase 3 |
| Compound Interest page | ~25 | Phase 3 |
| Portfolio pages (11 files) | ~80 | Phase 3 |
| Other pages (8 routes) | ~50 | Phase 3 |
| Other components (6 files) | ~20 | Phase 3 |
| **Total** | **~300** | — |

---

## Implementation Order

1. Create i18n infrastructure (Context, hook, `en.json`)
2. Create `zh-TW.json` and `zh-CN.json` translations
3. Wire `LanguageProvider` into `ClientProviders.tsx`
4. Add language dropdown to Settings modal Preferences tab
5. Translate Sidebar labels
6. Translate Settings modal tabs
7. Page-by-page string extraction (highest-traffic pages first: Mars → Portfolio → Compound)
8. Final pass on remaining pages and components
9. Dynamic `<html lang>` attribute
10. Playwright visual verification
