# Code Review — 2026-03-03 Sync v1
**Reviewer:** [CV]
**Date:** 2026-03-03 16:30 HKT

---

## Scope

All unpushed commits on `master` (7 commits ahead of `origin/master`):

| Commit | Description |
|--------|-------------|
| `7fcacbe` | feat(rebrand): Martian → Marffet (frontend, backend, i18n, localStorage) |
| `64b6aff` | docs: meeting notes + BOSS deployment checklist |
| `9614f2b` | fix: swap repo names (BOSS correction) |
| This session | fix: remaining Martian refs in viz.py, crawler_cb.py, main.py comments, 14 product docs, root README |

## Verdict: ✅ PASS

### Code Changes

| File | Change | Risk | Verdict |
|------|--------|------|---------|
| `compound/page.tsx` | PREMIUM+ gating on comparison mode | Low | ✅ Clean — uses `STORAGE_KEYS.PREMIUM`, `useEffect` for SSR safety |
| `constants.ts` | `martian_` → `marffet_` keys | Low | ✅ Single source of truth for keys |
| `LanguageContext.tsx` | Hardcoded `marffet_lang` | Low | ✅ Consistent |
| `portfolioService.ts` | `marffet_guest_data` | Low | ✅ |
| `mars/page.tsx` | `marffet_premium` | Low | ✅ |
| `page.tsx` | `marffet_default_page` | Low | ✅ |
| `AICopilot.tsx` | `marffet_chat_` prefix | Low | ✅ |
| `Sidebar.tsx` | Brand `MARFFET` + `marffet_premium` | Low | ✅ |
| `SettingsModal.tsx` | 7 localStorage keys + brand strings | Med | ✅ All correct |
| `ShareButton.tsx` | Default title "Marffet" | Low | ✅ |
| `layout.tsx` | OG metadata + Zeabur URL | Med | ✅ URL → `marffet-app.zeabur.app` |
| `doc/page.tsx` | Brand strings | Low | ✅ |
| `admin/page.tsx` | Footer brand | Low | ✅ |
| `ladder/page.tsx` | Share texts | Low | ✅ |
| `en.json`, `zh-TW.json`, `zh-CN.json` | 4 strings each | Low | ✅ |
| `main.py` | FastAPI title, CORS, health, comments | Med | ✅ All marffet-app/marffet-api |
| `auth.py` | Comment updates | Low | ✅ |
| `engines.py` | Docstring | Low | ✅ |
| `viz.py` | Page titles | Low | ✅ |
| `crawler_cb.py` | User-Agent `MarffetBot/1.0` | Low | ✅ |
| `backup.py` | GITHUB_REPO comment | Low | ✅ → `terranandes/marffet` |

### Residual "Martian" Scan Results

| Location | Status |
|----------|--------|
| Frontend `*.tsx` / `*.ts` | ✅ Clean (only "(Martian + Buffet)" etymology — intentional) |
| Frontend `*.json` i18n | ✅ Clean |
| Frontend `martian_banner.png` reference | ⚠️ File reference only — banner file not renamed (cosmetic, no user impact) |
| Backend `*.py` | ✅ Clean |
| Product docs `docs/product/` | ✅ Clean (2 historical refs in tasks.md and BOSS_TBD.md — intentional) |
| Root `README.md` | ✅ Clean |

### Build Verification

- **Frontend:** ✅ All 13 routes compile (exit code 0)
- **No TypeScript errors**
- **No import breakages**

### Risks & Recommendations

1. **`martian_banner.png`**: The OG image file is still named `martian_banner.png` in `public/`. Consider renaming to `marffet_banner.png` for full consistency — but this is cosmetic and low priority.
2. **localStorage Migration**: Existing users with `martian_*` keys will lose their settings (language, default page, API key, premium status). This is acceptable per BOSS decision but worth noting.
3. **Zeabur `.env` Update**: `FRONTEND_URL` and `GITHUB_REPO` env vars must be updated by BOSS on Zeabur dashboard after push.
