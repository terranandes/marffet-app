# AntiGravity Agents Code Review
**Date**: 2026-03-07 23:57 HKT
**Version**: v5
**Lead**: [CV] Code Verification Manager

## 1. Review Subject
- **Commits**: `24aec98` (SWR refactor) + `7b81786` (AbortError/AICopilot notch fix)
- **Base**: `4ec2fe3` (`origin/master`)
- **Scope**: Full delta between `origin/master` and `HEAD` (100 files in diff, 11 source files)

## 2. Source Code Changes (11 files, 235+/308−)

| File | Change | Verdict |
|------|--------|---------|
| `frontend/src/app/mars/page.tsx` | SWR refactor: useState/useEffect → useSWR | ✅ APPROVED |
| `frontend/src/app/race/page.tsx` | SWR refactor | ✅ APPROVED |
| `frontend/src/app/cb/page.tsx` | SWR refactor | ✅ APPROVED |
| `frontend/src/app/ladder/page.tsx` | SWR refactor | ✅ APPROVED |
| `frontend/src/app/trend/page.tsx` | SWR refactor | ✅ APPROVED |
| `frontend/src/app/portfolio/hooks/usePortfolioData.ts` | SWR refactor (portfolio data) | ✅ APPROVED |
| `frontend/src/app/template.tsx` | Removed (page transition logic moved to SWR) | ✅ APPROVED |
| `frontend/src/components/AICopilot.tsx` | Safe-area notch padding, h-[100dvh] | ✅ APPROVED |
| `frontend/src/lib/UserContext.tsx` | AbortError fix: 8s→15s timeout, explicit abort reason | ✅ APPROVED |
| `tests/ops_scripts/test_aibot_remote.py` | New test script | ✅ NOTED |
| `tests/ops_scripts/test_oauth_metadata.py` | New test script | ✅ NOTED |

## 3. Non-Source Files

| Category | Files | Verdict |
|----------|-------|---------|
| Meeting notes | 4 files (v1, v3 update, v4 new) | ✅ APPROVED |
| Code review notes | 2 files (v3 update, v4 new) | ✅ APPROVED |
| JIRA tickets | BUG-015, BUG-016 | ✅ APPROVED |
| Product docs | tasks.md, test_plan.md, BOSS_TBD.md | ✅ APPROVED |
| Screenshots/evidence | 9 files | ✅ NOTED |
| `.agent/scripts` | 16 new utility scripts (YAML validation, symlink checks) | ⚠️ SEE FINDING |
| `app/portfolio.db` | Binary SQLite update | ⚠️ NOTED |

## 4. Critical Finding: Root `node_modules/` Tracked in Git

**Severity**: ⚠️ MEDIUM
**Files**: `node_modules/.bin/js-yaml`, `node_modules/argparse/*`, `node_modules/js-yaml/*`
**Root Cause**: A root-level `package.json` was created (likely to support `.agent/scripts` YAML validation), and `bun install` populated `node_modules/`. The root `.gitignore` does not exclude root-level `node_modules/`.

**Impact**: Adds ~10KB of vendored npm packages to git history. Not harmful but violates clean-repo practices.

**Recommendation**:
1. Add `node_modules/` to root `.gitignore`
2. Run `git rm -r --cached node_modules/`
3. Commit the cleanup

## 5. Minor Tech Debt

- `catch (e: any)` in `UserContext.tsx` — should be `catch (e: unknown)` with type guard. Non-blocking.

## 6. Build Integrity
- Next.js Turbopack build: ✅ PASS (confirmed in v4 session)
- No TypeScript compilation errors
- No ESLint warnings on changed files

## 7. Decision
- **Status**: [APPROVED] (Source code changes)
- **Blocked**: `node_modules` cleanup recommended before push
- **Confidence**: HIGH
