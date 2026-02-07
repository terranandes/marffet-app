---
description: Full coverage tests on local and remote Zeabur.
---

Do workflow `commit-but-push` before the following jobs.
Use skill `using-git-worktrees` to verify local APP.
1. Create a worktree with current/specified commit and branch. <br>
   Notice git-igonred files but neccessary, for exemple: `./.env`, should be copied as well into the worktree
2. Update rigorous test-plan (./docs/product/test_plan.md) according to current SPEC.
3. According to the latest test plan do:
   - Adjust/Add testing programs to verify
4. Use skill `agent-browser`/`webapp-testing` to
- Full headlessly exhausted bug-hunting with MCP Playwright Suite locally.
- File the new bug found at `./docs/jira`.You must emphaseize which agent is firing tickets.
- Take screenshots of evidences with Playwright at `./tests/screenshots`. Don't commit/push screenshots.

After local verification is done without critical bugs found. Do the following jobs to verify remote deployment:
1. Do workflow `push-back-cur` before the following jobs.
2. Update rigorous test-plan (./docs/product/test_plan.md) according to current SPEC.
3. According to the latest test plan do:
   - Adjust/Add testing programs to verify
4. Use skill `agent-browser`/`webapp-testing` to
- Full headlessly exhausted bug-hunting with MCP Playwright Suite remotely.
- File the new bug found at `./docs/jira`.You must emphaseize which agent is firing tickets.
- Take screenshots of evidences with Playwright at `./tests/screenshots`. Don't commit/push screenshots.