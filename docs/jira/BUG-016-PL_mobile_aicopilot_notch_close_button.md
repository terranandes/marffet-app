# BUG-016: Mobile AICopilot Cannot Be Closed & Notch Interference
**Reporter**: [PL]
**Status**: CLOSED (Fixed via safe-area-inset-top padding in AICopilot.tsx)
**Severity**: High (Blocks core UX on mobile)

## Description
On mobile view, specifically iOS devices (iPhone), the AICopilot fullscreen modal cannot be closed. The 'X' (close) button is positioned too high and falls underneath the device's physical hardware notch or Dynamic Island (靈動島 / 前攝影頭). This makes the button unclickable and traps the user in the AI Copilot interface.

## Expected Behavior
The AICopilot header should respect the `env(safe-area-inset-top)` CSS variable to ensure that the header and all actionable buttons (like close or refresh) are pushed down below any hardware cutouts or status bars.

## Steps to Reproduce
1. Open the web app on an iPhone or an iOS simulator.
2. Open the AICopilot.
3. Attempt to click the 'X' close button in the top right corner.

## Proposed Strategy
- Modify `frontend/src/components/AICopilot.tsx`.
- Adjust the container or header classes to include `pt-[env(safe-area-inset-top)]` or similar safe-area padding.
- Verify the touch target size of the close button.
