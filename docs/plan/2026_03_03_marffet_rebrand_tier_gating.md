# Marffet Rebrand, Compound Interest Gating & Public Repo — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename the user-facing app brand from "Martian" to "Marffet" (Martian+Buffet), gate the Compound Interest comparison mode behind PREMIUM+, and create a public GitHub showcase repo `terranandes/marffet`.

**Architecture:** Three independent workstreams: (A) Feature gating is a 1-file frontend change, (B) rebranding is a multi-file find-and-replace across frontend components, i18n locales, backend metadata, and documentation, (C) public repo is an infra task using `gh` CLI. All changes stay on `master` in the private repo. The public repo is a brand new, completely separate repository.

**Tech Stack:** Next.js (frontend), FastAPI (backend), SQLite (DB), `gh` CLI (repo creation), i18n JSON locales.

**BOSS Decisions Already Locked:**
- ✅ App name: **Marffet** (Martian + Buffet)
- ✅ Public repo: `terranandes/marffet` (product showcase only, zero source code)
- ✅ Private repo: `terranandes/martian` (unchanged)
- ✅ Compound Interest comparison mode: PREMIUM+ only
- ✅ localStorage keys: Keep `martian_` prefix for backward compatibility (no migration)
- ✅ Zeabur service names (`martian-app`, `martian-api`): Out of scope (infra rename is separate)

---

## Task 1: Gate Compound Interest Comparison Mode (PREMIUM+)

**Files:**
- Modify: `frontend/src/app/compound/page.tsx`

**Step 1: Add `is_premium` state and read from localStorage**

At the top of the component (near existing `useState` calls), add:
```tsx
const [isPremium, setIsPremium] = useState(false);

useEffect(() => {
    setIsPremium(localStorage.getItem("martian_premium") === "true");
}, []);
```

**Step 2: Gate the "Comparison" mode toggle button**

Wrap the comparison button with a premium check. When a non-premium user clicks, show the comparison button as disabled or display a lock icon with a tooltip. The `setSettings({ ...settings, mode: "comparison" })` call should be conditional on `isPremium`.

Find the comparison toggle button (around line 222):
```tsx
<button onClick={() => setSettings({ ...settings, mode: "comparison" })} ...>
```

Replace with:
```tsx
<button
    onClick={() => isPremium ? setSettings({ ...settings, mode: "comparison" }) : null}
    disabled={!isPremium}
    className={`flex-1 py-1.5 text-xs font-bold rounded transition ${
        !isPremium
            ? "text-zinc-600 cursor-not-allowed"
            : settings.mode === "comparison"
                ? "bg-amber-500 text-black"
                : "text-zinc-400 hover:text-white"
    }`}
    title={!isPremium ? "Premium feature" : ""}
>
    {isPremium ? t('Compound.Comparison') : `🔒 ${t('Compound.Comparison')}`}
</button>
```

**Step 3: Verify locally**

1. Start the app: `./start_app.sh`
2. As a non-premium user, navigate to Compound Interest tab.
3. Confirm the "Comparison" button shows a 🔒 lock and is disabled.
4. Log in as a premium user, confirm the button is active and functional.

**Step 4: Commit**
```bash
git add frontend/src/app/compound/page.tsx
git commit -m "feat: gate compound interest comparison mode behind PREMIUM+"
```

---

## Task 2: Rebrand Frontend — User-Facing Strings

**Files:**
- Modify: `frontend/src/app/layout.tsx` (SEO metadata)
- Modify: `frontend/src/components/Sidebar.tsx` (logo, footer)
- Modify: `frontend/src/components/SettingsModal.tsx` (about section, feedback)
- Modify: `frontend/src/components/ShareButton.tsx` (share text)
- Modify: `frontend/src/app/doc/page.tsx` (about page)
- Modify: `frontend/src/app/admin/page.tsx` (admin footer)
- Modify: `frontend/src/app/ladder/page.tsx` (share texts)

### Replacement Map (User-Facing Only)

| Old String | New String |
|------------|-----------|
| `Martian Investment System` | `Marffet Investment System` |
| `Martian Investment` | `Marffet Investment` |
| `Project Martian` | `Project Marffet` |
| `Martian System` | `Marffet System` |
| `Martian AI Team` | `Marffet AI Team` |
| `Martian Top 50` | `Marffet Top 50` |
| `Martian investors` | `Marffet investors` |
| `MARTIAN` (Sidebar logo) | `MARFFET` |
| `siteName: "Martian"` | `siteName: "Marffet"` |

### Strings to KEEP (Internal / Backward Compat)

| String | Reason |
|--------|--------|
| `martian_api_key`, `martian_lang`, etc. | localStorage keys — changing breaks existing users |
| `martian-app.zeabur.app` | Zeabur domain — infra change is out of scope |
| `martian-api` | Backend service name |
| `MartianBot/1.0` | Web crawler User-Agent — cosmetic only, low priority |
| `terranandes/martian` | Private repo reference in `backup.py` |

**Step 1: Apply replacements to each file listed above**

For each file, perform the string replacements from the map. Be precise — only replace user-facing display strings, not infrastructure references.

**Step 2: Commit**
```bash
git add frontend/src/app/layout.tsx frontend/src/components/Sidebar.tsx \
       frontend/src/components/SettingsModal.tsx frontend/src/components/ShareButton.tsx \
       frontend/src/app/doc/page.tsx frontend/src/app/admin/page.tsx \
       frontend/src/app/ladder/page.tsx
git commit -m "feat(rebrand): rename user-facing 'Martian' to 'Marffet' in frontend components"
```

---

## Task 3: Rebrand i18n Locale Files

**Files:**
- Modify: `frontend/src/lib/i18n/locales/en.json`
- Modify: `frontend/src/lib/i18n/locales/zh-TW.json`
- Modify: `frontend/src/lib/i18n/locales/zh-CN.json`

### Replacement Map

Apply the same brand replacements from Task 2 inside each locale JSON file:
- `en.json`: 4 occurrences of "Martian" (FeedbackDesc, SignInDesc, Ladder.Subtitle, Trend.Subtitle)
- `zh-TW.json`: 4 occurrences
- `zh-CN.json`: 4 occurrences

**Step 1: Apply replacements**

**Step 2: Commit**
```bash
git add frontend/src/lib/i18n/locales/*.json
git commit -m "feat(rebrand): rename 'Martian' to 'Marffet' in i18n locale files"
```

---

## Task 4: Rebrand Backend Metadata

**Files:**
- Modify: `app/main.py` (FastAPI title, health endpoint)
- Modify: `app/engines.py` (docstring)

### Replacement Map

| File | Old | New |
|------|-----|-----|
| `app/main.py:123` | `title="Martian Investment System"` | `title="Marffet Investment System"` |
| `app/main.py:242` | `"service": "martian-backend"` | `"service": "marffet-backend"` |
| `app/main.py:1404` | `"service": "Martian API"` | `"service": "Marffet API"` |
| `app/engines.py:2` | `Backend Engines for Martian Investment System` | `Backend Engines for Marffet Investment System` |

**DO NOT change:**
- CORS origins (`martian-app.zeabur.app`, `martian-api.zeabur.app`) — these are live infrastructure URLs
- Cookie domain logic — infrastructure concern
- `backup.py` repo reference — private repo stays `terranandes/martian`

**Step 1: Apply replacements**

**Step 2: Commit**
```bash
git add app/main.py app/engines.py
git commit -m "feat(rebrand): rename backend metadata from 'Martian' to 'Marffet'"
```

---

## Task 5: Update Product Documentation

**Files:**
- Modify: `docs/product/README.md`
- Modify: `docs/product/README-zh-TW.md`
- Modify: `docs/product/README-zh-CN.md`
- Modify: `docs/product/datasheet.md`
- Modify: `docs/product/specification.md`
- Modify: `docs/product/social_media_promo.md`
- Modify: `README.md` (root)

### Replacement Strategy

Replace all user-facing "Martian" references with "Marffet" in product documentation. Keep technical references to the private repo name (`terranandes/martian`) unchanged.

**Step 1: Apply replacements**

**Step 2: Commit**
```bash
git add docs/product/*.md README.md
git commit -m "docs(rebrand): rename 'Martian' to 'Marffet' in product documentation"
```

---

## Task 6: Create Public Repo `terranandes/marffet`

**Prerequisites:** `gh` CLI is installed and authenticated.

**Step 1: Create the public repo**
```bash
gh repo create terranandes/marffet --public --description "Marffet Investment System — Taiwan Stock Market Analysis & Portfolio Management" --clone
```

**Step 2: Populate the repo structure**

```
marffet/                        # PUBLIC repo
├── README.md                   # Product showcase (EN)
├── README-zh-TW.md             # Traditional Chinese
├── README-zh-CN.md             # Simplified Chinese
├── LICENSE                     # MIT License
├── screenshots/                # App screenshots (to be captured)
│   ├── mars_strategy.png
│   ├── portfolio.png
│   ├── compound_interest.png
│   └── bar_chart_race.png
└── .github/
    └── FUNDING.yml             # GitHub Sponsor button
```

**Step 3: Create `.github/FUNDING.yml`**
```yaml
ko_fi: terranandes
buy_me_a_coffee: terranandes
```

**Step 4: Create `LICENSE` (MIT)**

**Step 5: Create `README.md`**
Copy and adapt content from `docs/product/README.md` (post-rebrand). Include:
- Product description (zero technical details)
- Feature highlights with screenshots
- Live app URL: `https://martian-app.zeabur.app` (until Zeabur domain rename)
- Sponsorship links

**Step 6: Create `README-zh-TW.md` and `README-zh-CN.md`**
Copy and adapt from `docs/product/README-zh-TW.md` and `docs/product/README-zh-CN.md`.

**Step 7: Commit and push**
```bash
cd marffet
git add -A
git commit -m "feat: initial public showcase for Marffet Investment System"
git push origin main
```

**Step 8: Verify**
- Visit `https://github.com/terranandes/marffet`
- Confirm FUNDING.yml creates the "Sponsor" button
- Confirm README renders correctly

---

## Task 7: Update `tasks.md` and Final Commit

**Files:**
- Modify: `docs/product/tasks.md`

**Step 1: Add Phase 25 completion entries**

Mark the completed items under Phase 25 and add references to this plan and meeting notes.

**Step 2: Final commit**
```bash
git add docs/product/tasks.md
git commit -m "docs: mark Phase 25 completion — Marffet rebrand, tier gating, public repo"
```

---

## Verification Checklist

| # | Check | How |
|---|-------|-----|
| 1 | Compound Interest comparison mode locked for free users | Start app, navigate to Compound Interest, verify 🔒 on comparison button |
| 2 | Compound Interest comparison mode works for premium users | Log in as premium, verify comparison toggle is active |
| 3 | Sidebar shows "MARFFET" instead of "MARTIAN" | Visual check |
| 4 | Page title shows "Marffet Investment System" | Check browser tab |
| 5 | Settings modal "About" section shows "Marffet" | Open Settings → About |
| 6 | i18n strings updated in all 3 languages | Switch language in Settings, verify no "Martian" in UI |
| 7 | Backend health endpoint returns "Marffet API" | `curl localhost:8000/` |
| 8 | Public repo exists at `github.com/terranandes/marffet` | Visit URL |
| 9 | GitHub Sponsor button appears on public repo | Visual check |
| 10 | localStorage keys still use `martian_` prefix | Check Application → Local Storage in DevTools |
