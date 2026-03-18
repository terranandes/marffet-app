# Chrome DevTools MCP Usage Guide

**Owner:** [PL] Project Leader
**Last Updated:** 2026-03-19

---

## Overview

Chrome DevTools MCP allows AI Agents to directly control your **currently open Chrome browser window**, including logged-in tabs, cookies, localStorage, and other full session states.

> [!IMPORTANT]
> This is different from the Playwright MCP! Playwright opens a completely new, isolated browser; Chrome DevTools MCP connects to **your currently used browser**.

---

## Use Cases

| Scenario | Recommended Tool |
| --- | --- |
| Automated E2E testing matrix (round7_full_suite.py) | **Playwright MCP** |
| Debugging Zeabur pages with logged-in accounts | **Chrome DevTools MCP** ✅ |
| Inspecting Network requests, Console errors | **Chrome DevTools MCP** ✅ |
| Performance Analysis (Performance Trace) | **Chrome DevTools MCP** ✅ |
| Testing public pages without login | Both Playwright or Chrome DevTools MCP |

---

## Setup Steps (One-time setup for Chrome 145+)

### Step 1: Enable Chrome Remote Debugging

1. Type in the Chrome address bar: `chrome://inspect/#remote-debugging`
2. Toggle on: **Allow remote debugging for this browser instance**

> [!TIP]
> Chrome 145+ supports this natively. No need for the `--remote-debugging-port=9222` flag nor the `--channel=beta` flag. No browser restart required.

### Step 2: MCP Configuration

Add to `~/.gemini/antigravity/mcp_config.json`:

```json
"chrome-devtools": {
  "command": "bunx",
  "args": [
    "-y",
    "chrome-devtools-mcp",
    "--autoConnect"
  ],
  "env": {}
}
```

> [!NOTE]
> `--autoConnect` is the key parameter that allows the MCP Server to automatically connect to an open Chrome instance.

### Step 3: Restart MCP Server

Reload the MCP configuration in your AntiGravity IDE.

### Step 4: Authorization

When an AI Agent needs to control the browser, Chrome will pop up a confirmation window:

```
Allow debugging session?
[Allow] [Deny]
```

Click **Allow** to let the AI start working.

---

## Actual Workflow Examples

### Scenario: Debugging with a logged-in account on Zeabur

1. **Boss** logs into `marffet-app.zeabur.app` in Chrome (using Google OAuth).
2. **Boss** finds a bug and tells the AI: "Connect to my Chrome and check why the Portfolio page is not loading data."
3. **AI** uses Chrome DevTools MCP to:
   - Read error messages in the Console log.
   - Inspect failed API requests in the Network panel.
   - Check the DOM state of React components.
   - Capture screenshots as bug report attachments.
4. **AI** modifies the code directly based on the findings.

### Scenario: Performance Analysis

```
Boss: "Run a Performance Trace on the Portfolio page for me and see where it is stuck."
AI → Chrome DevTools MCP → Record Performance Trace → Analyze results → Propose optimization suggestions.
```

---

## Security Precautions

> [!CAUTION]
> Chrome DevTools MCP has full access to the browser, including logged-in session cookies.
> - **Use only on a local development network.**
> - **Do not enable remote debugging on public Wi-Fi.**
> - **Disable the toggle at `chrome://inspect/#remote-debugging` when finished.**

---

## Comparison with Other Tools

| Feature | Playwright MCP | Chrome DevTools MCP |
| --- | --- | --- |
| Browser | Isolated Chromium instance | Your current Chrome browser |
| Session State | Fresh (No Cookies) | Full (Logged in / existing Cookies) |
| E2E Automated Testing | ✅ Best | ⚠️ Possible, but not the primary intent |
| Real-time Debugging | ❌ Cannot see your screen | ✅ Best |
| Performance Analysis | ❌ | ✅ Native support |
| Browser Restart Required | No | No (Chrome 145+) |
| Human Verification (Turnstile) | ❌ Usually blocked | ✅ Possible (since it's a real browser) |

---

## Reference Resources

- [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) — Official GitHub
- [NPM: chrome-devtools-mcp](https://www.npmjs.com/package/chrome-devtools-mcp) — v0.20.2+
- [Chrome Release Notes](https://developer.chrome.com/blog/) — Native remote debugging support
