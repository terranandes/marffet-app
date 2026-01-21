# BUG-005: Settings Button Selector mismatch

## Description
The automated test scripts `tests/bug_hunt.py` and `tests/full_verification.py` fail to find the Settings button using the locator `button[title="Settings"]`.

## Evidence
- Screenshot: `debug_settings_missing.png`
- Playwright Snapshot: Shows `button "Settings"` but likely missing the `title` attribute in the raw HTML.

## Suggested Fix
Update the button to include `title="Settings"` or update tests to use `page.get_by_role("button", name="Settings")`.

## Status
- **Closed / Resolved**

## Resolution
1. Added `aria-label="Settings"` and `data-testid="settings-button"` to the Settings button in `app/static/index.html`.
2. Updated `tests/full_verification.py` to use `[data-testid="settings-button"]` selector.
3. The button already had `title="Settings"` which `tests/bug_hunt.py` uses correctly.
