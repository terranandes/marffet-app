# Code Review: UI, AI Bot, and Mobile Features
**Date:** 2026-01-23
**Reviewer:** [CODE] (Agent)

## 1. Architecture Review
- **AICopilot Integration**: Implemented as a global component in `layout.tsx`. This is good for persistence across navigation.
- **State Management**: Using `localStorage` for API Keys and Preferences. Simple and effective for client-side settings, but keys are hardcoded in multiple files.
- **Component Structure**: `portfolio/page.tsx` is becoming monolithic (>1000 lines). The Mobile Card View added recently increases complexity.

## 2. Clean Code Review

### A. `frontend/src/components/AICopilot.tsx`
- **Issue**: Hardcoded `localStorage` keys (`martian_api_key`, `martian_chat_history`).
- **Issue**: Fallback URL `http://localhost:8000` is repeated.
- **Recommendation**: Extract constants.

### B. `frontend/src/components/SettingsModal.tsx`
- **Issue**: Duplciated `localStorage` keys matches those in `AICopilot.tsx`.
- **Recommendation**: Centralize keys in `src/lib/storage.ts` or `constants.ts`.

### C. `frontend/src/app/portfolio/page.tsx`
- **Issue**: **High Complexity**. File size violates "Single Responsibility" principle by mixing data fetching, desktop table rendering, and mobile card rendering.
- **Issue**: Code Duplication. Formatting logic (Red/Green colors, Currency formatting) is repeated between Desktop and Mobile views.
- **Recommendation**: Extract `PortfolioMobileCard` to a separate component.

### D. `frontend/src/app/race/page.tsx`
- **Status**: Clean. The compact view refactor was minimal and effective.
- **Note**: `getColor` function is duplicated in `RaceChart.tsx` (though `RaceChart.tsx` seems unused).

## 3. Refactoring Plan (Incremental)
1.  **Create Constants**: `frontend/src/lib/constants.ts` for storage keys.
2.  **Refactor Storage Usage**: Update `AICopilot` and `SettingsModal` to use constants.
3.  **Extract Component**: Move Mobile Portfolio Card to `frontend/src/components/portfolio/PortfolioCard.tsx`.

## 4. Testing
- **E2E**: Server currently unreachable, skipped.
- **Manual**: Logic verified via code inspection.

## 5. Conclusion
Code is functional but requires refactoring to maintainability. Proceeding with Step 3 (Incremental Refactor).
