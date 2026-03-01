---
description: Full coverage tests on local and remote Zeabur.
---

[PL] Commit necessary files, but push, including deployment requirements. before the following jobs.
Use skill `using-git-worktrees` to verify local APP.
1. Create a worktree with current/specified commit and branch. <br>
   Notice git-ignored files but necessary, for example: `./.env`, should be copied as well into the worktree
2. Update rigorous test-plan (./docs/product/test_plan.md for AntiGravity agents while ./docs/product/test_plan_gemini.md for Gemini CLI agents) according to current SPEC.
3. According to the latest test plan do:
   - Adjust/Add testing programs to verify
4. Use skill `agent-browser`/`webapp-testing` to
- Full headlessly exhausted bug-hunting with MCP Playwright Suite locally.
- File the new bug found at `./docs/jira`.You must emphasize which agent is firing tickets.
- Take screenshots of evidences with Playwright at (`./tests/evidence` for AntiGravity agents<br>
while `./tests_gemini/evidence` for Gemini CLI agents).<br>
Don't commit/push screenshots.