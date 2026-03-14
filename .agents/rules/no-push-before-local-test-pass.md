---
trigger: always_on
---

# Deployment & Verification Policy

1. **Local First**: modifying logic that can be tested locally? You MUST verify it locally (run app, run tests) before pushing.
2. **Remote Exception**: If a feature depends on the remote environment (e.g., OAuth, Zeabur variables, Nginx routing), you MAY push to `master` to verify, BUT you must:
   - Ensure the change is **non-destructive** (no DB wipes).
   - Monitor the build/deploy status immediately.
   - If it breaks, prioritize the fix immediately (Hotfix).
3. **Save Points**: You MAY push to `backup/*` or `feat/*` branches at any time to save progress without affecting Production (if Zeabur only deploys master).