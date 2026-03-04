# Plan: Public Repo `marffet-app` for Promotion

**Date:** 2026-03-04
**Owner:** [PL] / [PM]
**Scope:** Option A (Showcase-only), target audience: Potential Users/Investors

---

## Problem Statement

1. **Public repo `terranandes/marffet-app` exists but is empty** — needs to be populated with a polished showcase.
2. **README.md tier table is out of sync with `specification.md`** — 9+ cells are wrong.
3. **README-zh-TW.md and README-zh-CN.md lack tier tables** and are at v4.2 (spec is v5.0).
4. **Public repo needs language switcher links** — README must integrate zh-TW / zh-CN versions.

> [!IMPORTANT]
> The spec (`specification.md:55-70`) is the **single source of truth**. All README tier tables must match it exactly.

---

## Discrepancy Analysis (specification.md vs README.md)

| Feature | Spec (Truth) | README (Wrong) | Impact |
|---------|-------------|----------------|--------|
| Portfolio Groups (PREMIUM) | **20 max** | 30 | ❌ Overpromises |
| Targets per Group (PREMIUM) | **100 max** | 200 | ❌ Overpromises |
| Transactions/Target (PREMIUM) | **500 max** | 1,000 | ❌ Overpromises |
| AI Copilot (PREMIUM) | **Educator** | 💼 Wealth Manager | ❌ Wrong tier |
| AI Copilot (VIP) | **Wealth Manager** | 💼 Wealth Manager | ✅ OK |
| Bar Chart Race (GM) | **Full** | Advanced (CAGR) | ❌ Missing distinction |
| AI Copilot (GM) | **Full** | 💼 Wealth Manager | ❌ Missing distinction |
| CB/Rebalancing (GM) | **Full** | In-App + Email | ❌ Missing distinction |
| Server-Side Data row | **present** | missing | ❌ Missing row |
| Membership Injection row | **present** | missing | ❌ Missing row |

The zh-TW and zh-CN files have **no tier table at all** — only a 2-line prose summary that doesn't match spec either.

---

## Proposed Changes

### Part A: Sync README Tier Tables with Spec

---

#### [MODIFY] [README.md](file:///home/terwu01/github/marffet/docs/product/README.md)

1. Replace tier table (L97-111) with exact values from `specification.md:55-70`
2. Update `v5.0` → `v5.1` at bottom
3. Add language switcher links at top: `🌐 [繁體中文](./README-zh-TW.md) | [简体中文](./README-zh-CN.md)`

#### [MODIFY] [README-zh-TW.md](file:///home/terwu01/github/marffet/docs/product/README-zh-TW.md)

1. Replace the 2-line prose tier summary (L68-70) with the **full tier table** translated to Traditional Chinese
2. Update version from `v4.2` → `v5.1`
3. Add language switcher at top: `🌐 [English](./README.md) | [简体中文](./README-zh-CN.md)`

#### [MODIFY] [README-zh-CN.md](file:///home/terwu01/github/marffet/docs/product/README-zh-CN.md)

1. Replace the 2-line prose tier summary (L68-70) with the **full tier table** translated to Simplified Chinese
2. Update version from `v4.2` → `v5.1`
3. Add language switcher at top: `🌐 [English](./README.md) | [繁體中文](./README-zh-TW.md)`

---

### Part B: Public Repo Showcase Content

---

#### [NEW] Public repo `terranandes/marffet-app` structure:

```
marffet-app/
├── README.md              ← Copy of synced docs/product/README.md + screenshots
├── README-zh-TW.md        ← Copy of synced docs/product/README-zh-TW.md
├── README-zh-CN.md        ← Copy of synced docs/product/README-zh-CN.md
├── screenshots/           ← Auto-generated app screenshots
│   ├── mars_strategy.png
│   ├── compound_chart.png
│   ├── portfolio.png
│   ├── bar_chart_race.png
│   └── landing.png
└── LICENSE                ← Proprietary / All Rights Reserved
```

#### Steps:
1. Clone `terranandes/marffet-app` locally
2. Copy synced READMEs to root
3. Add hero section with screenshots to the English README
4. Generate screenshots via Playwright from the live app (`marffet-app.zeabur.app`)
5. Add GitHub repo description + topics (`fintech`, `investment`, `nextjs`, `ai`, `taiwan-stocks`, `backtesting`)
6. Push to origin

---

### Part C: Datasheet Sync (Minor)

#### [MODIFY] [datasheet.md](file:///home/terwu01/github/marffet/docs/product/datasheet.md)

- Verify tier table matches spec (quick audit — may already be correct since it was updated in Phase 25)

---

## Verification Plan

### Automated Checks
1. **Diff verification**: After editing, `diff` the tier table rows in all 3 READMEs against `specification.md:55-70` to confirm exact match
2. **Markdown lint**: Ensure tables render correctly (no broken pipes or alignment issues)

### Manual Verification
1. **BOSS reviews** the synced README.md tier table in GitHub preview
2. **BOSS reviews** the public repo `terranandes/marffet-app` on GitHub to confirm:
   - README renders correctly with screenshots
   - Language switcher links work (README ↔ zh-TW ↔ zh-CN)
   - Repo description and topics are set

### Browser Verification
1. Navigate to `https://github.com/terranandes/marffet-app` and visually confirm the README renders with:
   - Screenshots visible
   - Tier table correctly formatted
   - Language links functional

---

## Execution Order

1. ✏️ Sync `README.md` tier table with spec
2. ✏️ Add tier table + language links to `README-zh-TW.md`
3. ✏️ Add tier table + language links to `README-zh-CN.md`
4. 📸 Generate screenshots from live app
5. 📦 Populate public repo with synced READMEs + screenshots
6. 🔧 Set GitHub repo description and topics via `gh` CLI
7. ✅ Verify via browser
