# Bug: Automated Browser Environment Unstable

**Date**: 2026-01-24
**Reporter**: [CV]
**Priority**: High (Blocks Regression Testing)

## Description
The automated browser testing suite (`browser_subagent` using Playwright MCP) failed consistently with a `CDP port not responsive` error when attempting to connect to the local Chrome instance.
Additionally, local backend curl probe timed out after 5s.

## Error Log
```
failed to create browser context: failed to create browser instance: failed to connect to browser via CDP: http://127.0.0.1:9222. CDP port not responsive in 5s: playwright: connect ECONNREFUSED 127.0.0.1:9222
```

## Impact
- Unable to executing `test_plan.md` visual verification (TC-01 to TC-11).
- Unable to capture automated screenshots.
- Fallback to `curl` only verified HTTP status (Remote=OK, Local-Backend=Timeout).

## Suggested Fix
- Inspect local Chrome debug port settings.
- Ensure `google-chrome-stable` or Chromium is correctly installed and accessible by the MCP server.
