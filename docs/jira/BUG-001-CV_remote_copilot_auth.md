# BUG-001-CV_remote_copilot_auth

**Reporter:** [CV] Code Verification Manager
**Component:** AI Copilot Backend (Zeabur Production)
**Priority:** High (Core feature unavailable for non-premium users)
**Status:** ✅ CLOSED (2026-03-01) — Fixed: Configured Tier 1 Gemini Key, updated backend model logic to gemini-2.5-flash.

## Description
When executing `verify_task3_copilot.py` to test the `/api/chat` inference endpoint on `martian-api.zeabur.app` without providing a client API key, the server correctly falls back to its environment variable `GEMINI_API_KEY`. However, the Google Cloud Project backing that API key has the Generative Language API disabled.

## Error Trace
```json
{
  "error": "403 PERMISSION_DENIED. {'error': {'code': 403, 'message': 'Generative Language API has not been used in project 1009725210430 before or it is disabled...
}
```

## Expected Behavior
The AI Copilot should successfully respond to queries using the server's embedded key for guest/non-premium users as dictated by the `/test_plan` verification requirements. 

## Recommended Action
1. Log into Google Cloud Console for project `1009725210430`.
2. Enable the `Generative Language API` at the provided activation URL.
3. Alternatively, update the Zeabur Environment Variables (`GEMINI_API_KEY`) to a valid, active API key.
