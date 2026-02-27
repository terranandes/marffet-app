# BUG-119-UI: Transaction Date Input Calendar Style Missing

**Reporter:** [PL]
**Component:** Frontend (Portfolio Transaction Modal)
**Severity:** Minor
**Status:** OPEN

## Description
The user reported that the date input field in the "New Transaction" / "Edit Transaction" modal no longer displays or behaves with the expected calendar style ("cannot use calendar style, that was working"). The current implementation in `TransactionFormModal.tsx` uses a native HTML5 `<input type="date">`. 

## Potential Root Causes
1. **Dark Mode / CSS Reset Compatibility:** Since the application uses a dark theme (`bg-black/50`), webkit-native pseudo-elements like `::-webkit-calendar-picker-indicator` might be hard-to-see (rendered black on black) or stripped out entirely by a recent CSS reset/Tailwind update. 
2. **Browser Constraints:** The native date picker might have degraded usability depending on the browser (e.g. Chrome vs Firefox).

## Action Plan
1. Inspect `globals.css` or `index.css` for any `color-scheme: dark` or specific `::-webkit-calendar-picker-indicator` css overrides.
2. Ensure `color-scheme: dark;` is applied to the input or globally so the browser's native date picker adapts to the dark theme, making the calendar icon and popup legible.
3. If native remains glitchy, consider swapping to a lightweight customized date picker component, though CSS fix is preferred for simplicity.
