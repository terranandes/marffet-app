# Marffet — GitHub Showcase Guide
**Owner:** [PM]
**Version:** 1.0
**Date:** 2026-03-04

---

## 🔗 Repository Links

| Repository | Type | URL |
|:-----------|:-----|:----|
| **Public Showcase** | 📢 Public | [github.com/terranandes/marffet-app](https://github.com/terranandes/marffet-app) |
| **Source Code** | 🔒 Private | `github.com/terranandes/marffet` |
| **Live App** | 🌐 Production | [marffet-app.zeabur.app](https://marffet-app.zeabur.app) |

---

## 📦 Public Repo Contents

```
marffet-app/
├── README.md              ← English (hero section + screenshots + tier table)
├── README-zh-TW.md        ← 繁體中文 (Traditional Chinese)
├── README-zh-CN.md        ← 简体中文 (Simplified Chinese)
├── screenshots/           ← Dark-mode app screenshots (1920×1080)
│   ├── mars_strategy.png  ← Top 50 Survivors table
│   ├── compound_chart.png ← Compound Interest calculator
│   ├── bar_chart_race.png ← Dynamic BCR visualization
│   └── landing.png        ← Home page
└── LICENSE                ← All Rights Reserved (Proprietary)
```

### Language Switcher
All 3 README files are cross-linked via a 🌐 language switcher at the top:
- EN → zh-TW, zh-CN
- zh-TW → EN, zh-CN
- zh-CN → EN, zh-TW

---

## ⚙️ GitHub Repo Settings (Manual — BOSS)

> These need to be set via GitHub UI:
> **Go to** https://github.com/terranandes/marffet-app → ⚙️ (next to "About")

| Setting | Value |
|:--------|:------|
| **Description** | AI-powered investment simulator for Taiwan stocks — backtest strategies, track portfolios, compete on leaderboards |
| **Website** | `https://marffet-app.zeabur.app` |
| **Topics** | `fintech`, `investment`, `nextjs`, `ai`, `taiwan-stocks`, `backtesting`, `duckdb` |

---

## 📊 Showcase Highlights

### For Potential Users / Investors

| Highlight | Detail |
|:----------|:-------|
| **20+ years** of Taiwan stock history | TWSE + TPEx + Bond ETFs + Convertible Bonds |
| **< 200ms** calculation speed | DuckDB columnar engine + vectorized numpy math |
| **1,000+ stocks** in database | Daily prices from 2004–2026, 5M+ rows |
| **9 feature modules** | Mars Strategy, BCR, Compound, Portfolio, Trend, My Race, Cash Ladder, CB, AI Copilot |
| **5-tier membership** | Guest → Free → Premium → VIP → GM |
| **AI Copilot** | Powered by Google Gemini with tier-based personalities |
| **Multi-language** | English, 繁體中文, 简体中文 |
| **Cyberpunk UI** | Dark mode, glassmorphism, Framer Motion animations |

### Tech Stack (for developers who visit)

| Layer | Technology |
|:------|:-----------|
| Frontend | Next.js 16, React 18, ECharts, Framer Motion |
| Backend | FastAPI (Python 3.12), DuckDB |
| Auth | Google OAuth 2.0 |
| Hosting | Zeabur (Docker containers) |
| AI | Google Gemini 2.5 Flash |

---

## 🚫 Sensitive Words Policy

The following words must **never appear** in public-facing documents:

| Word | Why | Replacement |
|:-----|:----|:------------|
| ~~andes~~ | Private identifier | (omit or use "Marffet Team") |
| ~~MoneyCome~~ | Competitor reference | (omit — never mention) |
| ~~moneycome~~ | Competitor reference | (omit — never mention) |

> **Note**: The GitHub username `terranandes` is acceptable in URLs since it's the actual account name and cannot be changed. But standalone prose should never reference these words.

---

## 📋 Maintenance Checklist

When updating the public repo:

- [ ] Verify tier table matches `specification.md` (single source of truth)
- [ ] Ensure language switcher links are correct across all 3 READMEs
- [ ] Check for sensitive word leaks (`grep -i "andes\|moneycome"`)
- [ ] Regenerate screenshots if UI changes significantly
- [ ] Update version number if features change
- [ ] Never commit source code, `.env`, or backend logic to the public repo

---

## 📸 Screenshot Refresh Process

When UI changes require new screenshots:

1. Navigate to `https://marffet-app.zeabur.app` via Playwright
2. Set viewport to 1920×1080
3. Enter Guest mode
4. Visit each key page, wait for data, take screenshot
5. Save to `/tmp/marffet-app/screenshots/`
6. Commit and push to `terranandes/marffet-app`

---

*Last updated: 2026-03-04 by [PM]*
