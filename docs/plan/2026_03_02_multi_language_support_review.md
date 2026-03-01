# Multi-Language Support — Multi-Agent Design Review

**Date:** 2026-03-02
**Plan Reviewed:** `docs/plan/2026_03_02_multi_language_support.md`

---

## 1️⃣ Primary Designer (Lead Agent)

**Design:** Custom i18n using React Context + JSON translation files. No external dependencies. Language preference stored in `localStorage` (`martian_lang`), selectable from the Settings modal Preferences tab. Three locales: `en`, `zh-TW`, `zh-CN`.

**Decision Log:**
| # | Decision | Alternatives | Rationale |
|---|----------|-------------|-----------|
| 1 | Custom Context over `next-intl` | `next-intl`, `react-i18next` | All pages are `"use client"`, no SSR i18n needed. Zero-dep aligns with lean stack. |
| 2 | localStorage over URL-based locale | URL routing (`/en/mars`, `/zh-TW/mars`) | App is SPA-like with Settings modal control. No SEO need for locale URLs. |
| 3 | Phased rollout (3 phases) | Big-bang replacement | Reduces PR size, allows incremental QA. |
| 4 | Fallback chain: locale → en → key | Throw error on missing key | Graceful degradation. Missing translations show English, not broken UI. |

---

## 2️⃣ Skeptic / Challenger

### Objection 1: String interpolation for dynamic values
**Concern:** Custom approach may miss complex interpolation patterns like `Showing top {count} of {total} results`.
**Resolution:** ✅ Accepted. The `t(key, params)` function will replace `{param}` placeholders in strings. Simple template literal replacement covers all current use cases.

### Objection 2: Pluralization rules differ across languages
**Concern:** Chinese doesn't have plural forms, but English does. Will this cause issues?
**Resolution:** ✅ Accepted. Chinese doesn't differentiate singular/plural, so no pluralization engine needed. English strings can use simple conditional logic where needed (`{count} item(s)`).

### Objection 3: localStorage not SSR-safe
**Concern:** Layout component is a server component — can't read localStorage there.
**Resolution:** ✅ Accepted. `LanguageProvider` initializes with `"en"` as default, then reads localStorage in `useEffect` on mount. Brief flash of English is acceptable (same pattern used for `martian_premium`).

---

## 3️⃣ Constraint Guardian

### Performance
- JSON files: ~5KB per locale for ~300 strings. Negligible impact.
- All three locales can be bundled statically (import/require) — no async loading needed.
- Context re-render only triggers on language change (rate: virtually never during a session).

### Maintainability
- Adding a new language = copy `en.json`, translate, add to locale map. 1-file change.
- Adding a new string = add key to all 3 JSON files. Grep-able pattern.

### Security
- No user-input rendered via `t()`. Translation values are static JSON. No XSS risk.

**Verdict:** ✅ No constraints violated.

---

## 4️⃣ User Advocate

### UX Observation 1: Language selector must use native names
**Concern:** Don't show "Chinese (Traditional)" — show "繁體中文" so Chinese users can find it.
**Resolution:** ✅ Incorporated. Dropdown will show: 🇺🇸 English, 🇹🇼 繁體中文, 🇨🇳 简体中文.

### UX Observation 2: No page reload on language switch
**Concern:** Users expect instant language change without reload.
**Resolution:** ✅ React Context re-render is instant. No reload needed.

### UX Observation 3: Financial data must stay untranslated
**Concern:** Stock names (台積電), prices ($NT90,629,825), and percentages must NOT be translated or reformatted.
**Resolution:** ✅ Only UI labels, buttons, headers, and messages are translated. Financial data passes through unchanged.

**Verdict:** ✅ UX approved.

---

## 5️⃣ Integrator / Arbiter

### Final Disposition: **APPROVED** ✅

All reviewer agents have been invoked. All objections resolved. Decision log is complete.

The custom i18n approach is sound for this project's scale (300 strings, 3 languages, all-client rendering). The phased rollout strategy (Infrastructure → Settings/Sidebar → Pages) minimizes risk and allows incremental verification.

**Proceed to implementation.**

---

## Exit Criteria Checklist

- [x] Understanding Lock completed
- [x] All reviewer agents invoked (Skeptic, Guardian, Advocate)
- [x] All objections resolved or explicitly accepted
- [x] Decision Log complete (4 decisions logged)
- [x] Arbiter declared design acceptable
