---
description: Create project plan using project-planner agent.
---

# /plan - Project Planning Mode <br>
No code writing - only plan file generation.

$ARGUMENTS

---
Steps:
1. Use skill `brainstorming` to conceive how/what to achieve $ARGUMENTS
2. Use skill `writing-plans` to plan $ARGUMENTS according to previous brainstorming result
3. Write down the plan so far in to `./docs/plan`.
4. Use skill `multi-agent-brainstorming` to review previously created plan
5. Write down the plan-reivew in to `./docs/plan`.